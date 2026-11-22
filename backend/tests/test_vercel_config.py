import json
from pathlib import Path

from app.main import SECURITY_HEADERS

# On Vercel the CDN serves the frontend, so the page itself gets its headers from vercel.json.
CONFIG = json.loads((Path(__file__).parents[2] / "vercel.json").read_text(encoding="utf-8"))


def test_every_page_on_vercel_gets_the_apps_security_headers() -> None:
    every_path = next(rule for rule in CONFIG["headers"] if rule["source"] == "/(.*)")
    sent = {header["key"]: header["value"] for header in every_path["headers"]}
    assert sent == SECURITY_HEADERS


def test_the_api_goes_to_the_backend_and_the_rest_to_the_frontend() -> None:
    assert CONFIG["rewrites"] == [
        {"source": "/api/(.*)", "destination": {"service": "backend"}},
        {"source": "/(.*)", "destination": {"service": "frontend"}},
    ]
