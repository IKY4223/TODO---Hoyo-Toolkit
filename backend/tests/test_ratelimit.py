import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.ratelimit import RateLimiter, client_key
from app.showcase import api as showcase_api


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def request_from(host: str | None, headers: dict[str, str] | None = None) -> Request:
    client = (host, 50000) if host else None
    raw = [(name.lower().encode(), value.encode()) for name, value in (headers or {}).items()]
    return Request({"type": "http", "client": client, "headers": raw})


def test_allows_the_limit_then_reports_the_wait() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=3, window=60, clock=clock)
    assert [limiter.seconds_until_allowed("a") for _ in range(3)] == [0, 0, 0]
    clock.now = 20
    assert limiter.seconds_until_allowed("a") == 40


def test_a_refused_request_does_not_extend_the_wait() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=1, window=60, clock=clock)
    limiter.seconds_until_allowed("a")
    clock.now = 30
    limiter.seconds_until_allowed("a")
    clock.now = 60
    assert limiter.seconds_until_allowed("a") == 0


def test_clients_are_counted_separately() -> None:
    limiter = RateLimiter(limit=1, window=60)
    assert limiter.seconds_until_allowed("a") == 0
    assert limiter.seconds_until_allowed("b") == 0
    assert limiter.seconds_until_allowed("a") > 0


def test_full_table_refuses_new_clients_instead_of_growing() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=5, window=60, clock=clock, max_clients=2)
    assert limiter.seconds_until_allowed("a") == 0
    assert limiter.seconds_until_allowed("b") == 0
    assert limiter.seconds_until_allowed("c") > 0
    assert limiter.seconds_until_allowed("a") == 0  # known clients are not affected

    clock.now = 60  # finished windows make room
    assert limiter.seconds_until_allowed("c") == 0


def test_clear_forgets_every_client() -> None:
    limiter = RateLimiter(limit=1, window=60)
    limiter.seconds_until_allowed("a")
    limiter.clear()
    assert limiter.seconds_until_allowed("a") == 0


@pytest.mark.parametrize(
    ("host", "key"),
    [
        ("203.0.113.7", "203.0.113.7"),
        # One subscriber holds a whole IPv6 /64, so every address in it is one client.
        ("2001:db8:1:2:aaaa:bbbb:cccc:dddd", "2001:db8:1:2::/64"),
        ("2001:db8:1:2::1", "2001:db8:1:2::/64"),
        ("::ffff:203.0.113.7", "203.0.113.7"),
        ("testclient", "testclient"),
        (None, "unknown"),
    ],
)
def test_client_key(host: str | None, key: str) -> None:
    assert client_key(request_from(host)) == key


def test_endpoint_answers_429_with_the_wait_once_the_limit_is_spent() -> None:
    client = TestClient(app)
    url = "/api/showcase/12345"  # malformed, so Enka is never asked
    statuses = [client.get(url).status_code for _ in range(showcase_api.limiter.limit)]
    assert statuses == [422] * showcase_api.limiter.limit

    refused = client.get(url)
    assert refused.status_code == 429
    assert 1 <= int(refused.headers["Retry-After"]) <= 60
    assert "Too many requests" in refused.json()["detail"]


def test_each_tool_has_its_own_limit() -> None:
    client = TestClient(app)
    for _ in range(showcase_api.limiter.limit + 1):
        client.get("/api/showcase/12345")
    forecast = client.get(
        "/api/wishes/forecast", params={"pity": 0, "guaranteed": True, "copies": 1, "pulls": 1}
    )
    assert forecast.status_code == 200


PROXY = "10.0.0.1"  # every visitor arrives from the host's proxy


def test_a_client_ip_header_is_ignored_unless_the_host_names_it() -> None:
    assert client_key(request_from(PROXY, {"CF-Connecting-IP": "203.0.113.7"})) == PROXY


@pytest.mark.parametrize(
    ("value", "key"),
    [
        ("203.0.113.7", "203.0.113.7"),
        (" 203.0.113.7 ", "203.0.113.7"),
        ("2001:db8:1:2::1", "2001:db8:1:2::/64"),
        ("not an address", PROXY),  # garbage counts against the proxy, as before
        ("", PROXY),
    ],
)
def test_the_named_header_says_who_the_visitor_is(
    monkeypatch: pytest.MonkeyPatch, value: str, key: str
) -> None:
    monkeypatch.setenv("CLIENT_IP_HEADER", "CF-Connecting-IP")
    assert client_key(request_from(PROXY, {"CF-Connecting-IP": value})) == key


def test_without_the_named_header_the_peer_is_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLIENT_IP_HEADER", "CF-Connecting-IP")
    assert client_key(request_from(PROXY)) == PROXY
