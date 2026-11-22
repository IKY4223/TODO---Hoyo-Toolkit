"""Trying another artifact in a slot: the stats it would give and the damage they deal."""

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.damage.artifacts import set_change, swap
from app.main import app
from app.showcase.enka import parse
from app.showcase.gamedata import GAMEDATA
from app.showcase.models import Stat, StatKey

client = TestClient(app)
SHOWCASE = parse("700000001", (Path(__file__).parent / "fixtures/enka_showcase.json").read_bytes())[
    0
]
GANYU = SHOWCASE.characters[1]
STATS = {stat.key: stat.value for stat in GANYU.stats}
BASE = {stat.key: stat.value for stat in GANYU.base_stats}


def _stats(artifact_slot: str) -> list[Stat]:
    artifact = next(item for item in GANYU.artifacts if item.slot == artifact_slot)
    return [artifact.main, *artifact.subs]


def test_base_stats_come_from_the_showcase() -> None:
    # Ganyu's base ATK (her own and Amos' Bow's) is 942.9; 2249 is after every bonus.
    assert BASE[StatKey.ATK] == pytest.approx(942.92, abs=0.01)
    assert BASE[StatKey.HP] == pytest.approx(9796.73, abs=0.01)
    assert BASE[StatKey.DEF] == pytest.approx(630.21, abs=0.01)


GLADIATOR, NOBLESSE = 15001, 15007  # 2-piece: ATK +18%; Elemental Burst DMG +20%, not a stat


def test_a_set_keeps_its_bonus_when_one_piece_gives_way_to_another_of_it() -> None:
    assert set_change([GLADIATOR, GLADIATOR, 0], GLADIATOR, GLADIATOR) == []


def test_breaking_a_two_piece_set_takes_its_bonus_away() -> None:
    assert set_change([GLADIATOR, GLADIATOR, NOBLESSE], GLADIATOR, NOBLESSE) == [
        Stat(StatKey.ATK_PERCENT, -0.18)
    ]


def test_completing_a_two_piece_set_adds_its_bonus() -> None:
    assert set_change([GLADIATOR, NOBLESSE], None, GLADIATOR) == [Stat(StatKey.ATK_PERCENT, 0.18)]


def test_a_set_whose_bonus_is_no_stat_adds_nothing() -> None:
    assert set_change([NOBLESSE], None, NOBLESSE) == []


def test_putting_the_same_artifact_back_changes_nothing() -> None:
    sands = _stats("sands")
    assert swap(STATS, BASE, sands, sands) == pytest.approx(STATS)


def test_percent_stats_grow_from_the_base_and_others_add_up() -> None:
    sands = _stats("sands")  # ATK 46.6%, with DEF 39, HP 239, CRIT DMG 21.8%, CRIT Rate 7%
    other = [Stat(StatKey.ELEMENTAL_MASTERY, 187), Stat(StatKey.CRIT_RATE, 0.1)]
    result = swap(STATS, BASE, sands, other)
    assert result[StatKey.ATK] == pytest.approx(STATS[StatKey.ATK] - 0.466 * BASE[StatKey.ATK])
    assert result[StatKey.DEF] == pytest.approx(STATS[StatKey.DEF] - 39)
    assert result[StatKey.HP] == pytest.approx(STATS[StatKey.HP] - 239)
    assert result[StatKey.ELEMENTAL_MASTERY] == pytest.approx(
        STATS[StatKey.ELEMENTAL_MASTERY] + 187
    )
    assert result[StatKey.CRIT_RATE] == pytest.approx(STATS[StatKey.CRIT_RATE] - 0.07 + 0.1)
    assert result[StatKey.CRIT_DMG] == pytest.approx(STATS[StatKey.CRIT_DMG] - 0.218)


def test_a_goblet_of_another_element_moves_the_bonus() -> None:
    result = swap(STATS, BASE, _stats("goblet"), [Stat(StatKey.PYRO_DMG, 0.466)])
    assert result[StatKey.CRYO_DMG] == pytest.approx(0, abs=1e-6)  # Enka sends float32
    assert result[StatKey.PYRO_DMG] == pytest.approx(0.466)


def _artifact(item: Any) -> dict[str, Any]:
    return {
        "slot": item.slot,
        "set_id": item.set_id,
        "main": {"key": item.main.key, "value": item.main.value},
        "subs": [{"key": sub.key, "value": sub.value} for sub in item.subs],
    }


REQUEST: dict[str, Any] = {
    "level": GANYU.level,
    "stats": [{"key": stat.key, "value": stat.value} for stat in GANYU.stats],
    "scalings": [{"stat": "atk", "multiplier": 2.176}],
    "bonus": "cryo_dmg",
    "reaction": "none",
    "enemy_level": 90,
    "enemy_resistance": 0.1,
    "base_stats": [{"key": stat.key, "value": stat.value} for stat in GANYU.base_stats],
    "equipped": [_artifact(item) for item in GANYU.artifacts],
    "candidates": [_artifact(item) for item in SHOWCASE.characters[0].artifacts],
}


def test_answers_the_damage_now_and_with_each_candidate() -> None:
    response = client.post("/api/damage/artifacts", json=REQUEST)
    assert response.status_code == 200
    body = response.json()
    now = client.post("/api/damage", json=REQUEST).json()
    assert body["current"] == pytest.approx(now)
    assert len(body["candidates"]) == len(REQUEST["candidates"])
    # Her own goblet swapped for itself would deal what she deals now.
    same = client.post(
        "/api/damage/artifacts", json={**REQUEST, "candidates": [REQUEST["equipped"][3]]}
    ).json()
    assert same["candidates"][0] == pytest.approx(now)


@pytest.mark.parametrize(
    "override",
    [
        {"candidates": []},
        {"candidates": [REQUEST["equipped"][0]] * 61},
        {"equipped": [REQUEST["equipped"][0]] * 6},
        {"base_stats": [{"key": "atk", "value": 1}] * 4},
        {"base_stats": [{"key": "atk", "value": -1}]},
        {"base_stats": [{"key": "crit_rate", "value": 1}]},
        {"base_stats": []},
        {"base_stats": [{"key": "atk", "value": 900}] * 3},
        {"candidates": [{**REQUEST["equipped"][0], "subs": [REQUEST["equipped"][0]["main"]] * 5}]},
        {"candidates": [{**REQUEST["equipped"][0], "slot": "hat"}]},
        {"candidates": [{**REQUEST["equipped"][0], "set_id": -1}]},
        {"candidates": [{**REQUEST["equipped"][0], "set_id": 1_000_001}]},
    ],
    ids=[
        "no candidates",
        "too many",
        "six equipped",
        "four bases",
        "negative base",
        "base crit",
        "no bases",
        "one base thrice",
        "five subs",
        "slot",
        "negative set id",
        "set id too large",
    ],
)
def test_rejects_requests_no_showcase_can_make(override: dict[str, Any]) -> None:
    assert client.post("/api/damage/artifacts", json={**REQUEST, **override}).status_code == 422


def test_a_swap_that_breaks_a_set_loses_its_bonus() -> None:
    equipped = [
        {**item, "set_id": GLADIATOR if index < 2 else 0}  # two pieces
        for index, item in enumerate(REQUEST["equipped"])
    ]
    same_set, other_set = equipped[0], {**equipped[0], "set_id": 0}
    body = client.post(
        "/api/damage/artifacts",
        json={**REQUEST, "equipped": equipped, "candidates": [same_set, other_set]},
    ).json()
    assert body["candidates"][0] == pytest.approx(body["current"])
    # The same piece without the set: Gladiator's ATK +18% of her base is gone, nothing else.
    weaker = {**STATS, StatKey.ATK: STATS[StatKey.ATK] - 0.18 * BASE[StatKey.ATK]}
    expected = client.post(
        "/api/damage",
        json={**REQUEST, "stats": [{"key": key, "value": value} for key, value in weaker.items()]},
    ).json()
    assert body["candidates"][1] == pytest.approx(expected)


def test_an_artifact_sent_without_its_set_counts_as_no_set() -> None:
    # Clients from before set ids leave the field out; the trial still answers.
    bare = [
        {key: value for key, value in item.items() if key != "set_id"}
        for item in REQUEST["equipped"]
    ]
    response = client.post(
        "/api/damage/artifacts", json={**REQUEST, "equipped": bare, "candidates": bare[:1]}
    )
    assert response.status_code == 200


def test_the_showcase_gives_each_artifact_its_set() -> None:
    assert {item.set_id for item in GANYU.artifacts} <= {int(key) for key in GAMEDATA.sets}
