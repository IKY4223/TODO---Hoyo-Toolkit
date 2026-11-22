"""The app with Enka.Network and HoYoverse replaced by test fixtures, for the browser tests.

Run: STATIC_DIR=../frontend/dist uv run python -m tests.e2e_server <port>
"""

import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import uvicorn

from app.main import app
from app.showcase import api
from app.showcase.enka import EnkaError
from app.showcase.gamedata import GAMEDATA
from app.starrail import api as starrail_api
from app.wishes import api as wishes_api
from tests.gacha_fixture import body

FIXTURE = (Path(__file__).parent / "fixtures" / "enka_showcase.json").read_bytes()
STARRAIL_FIXTURE = (Path(__file__).parent / "fixtures" / "enka_starrail.json").read_bytes()
MISSING_UID = "404000000"
CATALYST_UID = "600000006"  # Ganyu's build worn by Lisa, so a catalyst user is in the showcase
LISA = "10000006"
CRYO_BONUS, ELECTRO_BONUS = "46", "41"  # Enka's fight prop ids
ENKA_NOT_FOUND = 404


def as_lisa(fixture: bytes) -> bytes:
    raw = json.loads(fixture)
    avatar = raw["avatarInfoList"][1]
    avatar["avatarId"] = int(LISA)
    levels = list(avatar["skillLevelMap"].values())
    talents = GAMEDATA.characters[LISA].talents
    avatar["skillLevelMap"] = {
        str(talent): level for (talent, _), level in zip(talents, levels, strict=True)
    }
    props = avatar["fightPropMap"]
    props[ELECTRO_BONUS], props[CRYO_BONUS] = props[CRYO_BONUS], 0
    return json.dumps(raw).encode()


def fetch(uid: str) -> bytes:
    if uid == MISSING_UID:
        raise EnkaError(ENKA_NOT_FOUND)
    return as_lisa(FIXTURE) if uid == CATALYST_UID else FIXTURE


def fetch_history(url: str) -> bytes:
    params = parse_qs(urlsplit(url).query)
    return body(params["gacha_type"][0], params["end_id"][0])


def fetch_starrail(uid: str) -> bytes:
    if uid == MISSING_UID:
        raise EnkaError(ENKA_NOT_FOUND)
    return STARRAIL_FIXTURE


app.dependency_overrides[api.get_fetch] = lambda: fetch
app.dependency_overrides[starrail_api.get_fetch] = lambda: fetch_starrail
app.dependency_overrides[wishes_api.get_history_fetch] = lambda: fetch_history
# The whole suite arrives from one address within a minute.
api.limiter.limit = 10_000

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]), log_level="warning")
