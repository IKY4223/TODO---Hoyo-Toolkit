import asyncio
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from app.main import LimitBody, app
from app.wishes.api import MAX_LINK_LENGTH

client = TestClient(app)


@pytest.mark.parametrize("url", ["/api/health", "/api/nowhere", "/api/showcase/12345"])
def test_every_response_limits_what_a_page_may_load(url: str) -> None:
    headers = client.get(url).headers
    policy = headers["Content-Security-Policy"]
    assert "default-src 'self'" in policy
    assert "img-src 'self' https://enka.network" in policy  # icons come from Enka's image host
    assert "frame-ancestors 'none'" in policy
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Referrer-Policy"] == "no-referrer"


def test_browsers_keep_to_https_for_a_year() -> None:
    assert client.get("/api/health").headers["Strict-Transport-Security"] == "max-age=31536000"


@pytest.mark.parametrize("url", ["/docs", "/redoc", "/openapi.json"])
def test_the_api_docs_are_not_served(url: str) -> None:
    assert client.get(url).status_code == 404


VISITED_OVER_HTTP = {"CF-Visitor": '{"scheme":"http"}'}  # Cloudflare's note of the visitor's scheme


def test_a_visit_over_http_moves_to_https() -> None:
    response = client.get("/api/nowhere?x=1", headers=VISITED_OVER_HTTP, follow_redirects=False)
    assert response.status_code == 308
    assert response.headers["Location"] == "https://testserver/api/nowhere?x=1"


def test_the_move_to_https_comes_before_the_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SITE_PASSWORD", "test-only")
    response = client.get("/", headers=VISITED_OVER_HTTP, follow_redirects=False)
    assert response.status_code == 308  # a 401 here would have the password sent in clear


@pytest.mark.parametrize(
    "headers",
    [{}, {"CF-Visitor": '{"scheme":"https"}'}, {"CF-Visitor": "garbage"}, {"CF-Visitor": "[1]"}],
)
def test_without_a_sign_of_http_nothing_moves(headers: dict[str, str]) -> None:
    assert client.get("/api/nowhere", headers=headers, follow_redirects=False).status_code == 404


def test_the_health_check_answers_over_http_too() -> None:
    response = client.get("/api/health", headers=VISITED_OVER_HTTP, follow_redirects=False)
    assert response.status_code == 200


FORECAST = "/api/starrail/relics/forecast"


def test_a_body_declared_too_large_is_refused_unread() -> None:
    response = client.post(FORECAST, content=b"{" + b" " * 70_000 + b"}")
    assert response.status_code == 413


def test_a_chunked_body_is_refused_once_it_grows_too_large() -> None:
    def chunks() -> Iterator[bytes]:
        for _ in range(20):
            yield b" " * 10_000

    response = client.post(FORECAST, content=chunks(), headers={"Content-Type": "application/json"})
    assert response.status_code == 413


def test_the_largest_request_the_site_sends_still_fits() -> None:
    link = "ж" * MAX_LINK_LENGTH  # JSON escapes each letter to six bytes
    body = {"link": link, "banner": "301", "end_id": "1"}
    assert client.post("/api/wishes/history", json=body).status_code == 400  # no link in it


def _run(messages: list[Message], scope_type: str = "http") -> tuple[list[Message], list[Message]]:
    """Runs LimitBody around an app that reads twice; returns what it read and what was sent."""
    incoming = iter(messages)
    read: list[Message] = []
    sent: list[Message] = []

    async def receive() -> Message:
        return next(incoming)

    async def send(message: Message) -> None:
        sent.append(message)

    async def inner(_scope: Scope, receive: Receive, _send: Send) -> None:
        read.extend([await receive(), await receive()])

    asyncio.run(LimitBody(inner)({"type": scope_type, "headers": []}, receive, send))
    return read, sent


def test_the_app_reads_the_body_once_then_the_client_as_usual() -> None:
    parts: list[Message] = [
        {"type": "http.request", "body": b"ab", "more_body": True},
        {"type": "http.request", "body": b"c"},
        {"type": "http.disconnect"},
    ]
    read, _ = _run(parts)
    assert read == [
        {"type": "http.request", "body": b"abc", "more_body": False},
        {"type": "http.disconnect"},
    ]


def test_a_client_that_leaves_mid_body_gets_nothing() -> None:
    read, sent = _run([{"type": "http.disconnect"}])
    assert (read, sent) == ([], [])


def test_other_connections_pass_untouched() -> None:
    events: list[Message] = [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]
    read, _ = _run(events, scope_type="lifespan")
    assert read == events
