import base64
import binascii
import json
import math
import os
import secrets
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.damage.api import router as damage_router
from app.ratelimit import RateLimiter, client_key
from app.showcase.api import router as showcase_router
from app.starrail.api import characters_router, relics_router
from app.starrail.api import router as starrail_router
from app.wishes.api import router as wishes_router

# No docs pages: they load scripts from a CDN past the site's policy. The frontend's types come
# from app.openapi(), which works without them.
app = FastAPI(title="HoYo Toolkit API", docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(damage_router)
app.include_router(showcase_router)
app.include_router(starrail_router)
app.include_router(relics_router)
app.include_router(characters_router)
app.include_router(wishes_router)

SECURITY_HEADERS = {
    # No includeSubDomains: the site lives on the host's shared domain.
    "Strict-Transport-Security": "max-age=31536000",
    # Scripts, styles and requests only from this origin; icons also from Enka's image host.
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' https://enka.network; object-src 'none'; "
        "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",  # the image host must not learn which page asked
    # Private until the launch checklist in CLAUDE.md is done: search engines must not list it.
    "X-Robots-Tag": "noindex, nofollow",
}
# A test deploy can ask for a password: set SITE_PASSWORD on the host. The host's health check
# must still reach the app.
OPEN_PATHS = ("/api/health",)
# Wrong passwords a client may try in a minute, so the one shared password cannot be guessed.
password_failures = RateLimiter(limit=10, window=60)
# The largest request the site sends, a wish history page pasted in Cyrillic, is about 30 kB.
MAX_BODY_BYTES = 64 * 1024
TOO_LARGE = "The request is too large."


def _password_given(request: Request, password: str) -> bool:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "basic":
        return False
    try:
        given = base64.b64decode(token, validate=True).decode().partition(":")[2]
    except (binascii.Error, UnicodeDecodeError):
        return False
    return secrets.compare_digest(given.encode(), password.encode())


@app.middleware("http")
async def ask_for_password(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    password = os.environ.get("SITE_PASSWORD", "")
    if not password or request.url.path in OPEN_PATHS:
        return await call_next(request)
    client = client_key(request)
    # Checked before the password, so a client out of guesses learns nothing from one more.
    wait = password_failures.seconds_until_spent_clears(client)
    if wait > 0:
        return Response(status_code=429, headers={"Retry-After": str(math.ceil(wait))})
    if _password_given(request, password):
        return await call_next(request)
    if "Authorization" in request.headers:  # a browser's first request only asks for a password
        password_failures.seconds_until_allowed(client)
    return Response(
        status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="HoYo Toolkit", charset="UTF-8"'},
    )


class LimitBody:
    """Refuses a request body over MAX_BODY_BYTES, whether declared up front or sent in chunks."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        too_large = JSONResponse({"detail": TOO_LARGE}, status_code=413)
        declared = Headers(scope=scope).get("content-length", "")
        if declared.isdigit() and int(declared) > MAX_BODY_BYTES:
            await too_large(scope, receive, send)
            return
        # Read the whole body first: it is small, and an error raised inside `receive` would reach
        # the route as a generic 400.
        body = b""
        more = True
        while more:
            message = await receive()
            if message["type"] != "http.request":
                return  # the client left
            body += message.get("body", b"")
            more = message.get("more_body", False)
            if len(body) > MAX_BODY_BYTES:
                await too_large(scope, receive, send)
                return
        replayed = False

        async def replay() -> Message:
            nonlocal replayed
            if replayed:
                return await receive()
            replayed = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay, send)


app.add_middleware(LimitBody)


def _visited_over_http(request: Request) -> bool:
    # The app sees plain http from the host's proxy whatever the visitor used, so it goes by the
    # scheme Cloudflare notes; without that note nothing moves, which cannot loop.
    try:
        visitor = json.loads(request.headers.get("CF-Visitor", "{}"))
    except ValueError:
        return False
    return isinstance(visitor, dict) and visitor.get("scheme") == "http"


# Defined after the password check, so it runs first: a password must never be asked over http.
@app.middleware("http")
async def move_to_https(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    if request.url.path not in OPEN_PATHS and _visited_over_http(request):
        return RedirectResponse(str(request.url.replace(scheme="https")), status_code=308)
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    response.headers.update(SECURITY_HEADERS)
    return response


@app.exception_handler(RequestValidationError)
async def report_invalid_request(_request: Request, error: RequestValidationError) -> JSONResponse:
    # The default handler echoes the rejected input back and crashes when that input is NaN,
    # which a JSON response cannot carry.
    problems = [
        {field: value for field, value in problem.items() if field != "input"}
        for problem in error.errors()
    ]
    return JSONResponse({"detail": jsonable_encoder(problems)}, status_code=422)


class Health(BaseModel):
    status: Literal["ok"]


@app.get("/api/health")
def health() -> Health:
    return Health(status="ok")


# The Docker image ships the built frontend; in dev Vite serves it instead.
static_dir = Path(os.environ.get("STATIC_DIR", "static"))
if static_dir.is_dir():
    # Mounted last so it never shadows /api routes.
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
