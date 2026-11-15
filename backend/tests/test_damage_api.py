from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
URL = "/api/damage"
VALID: dict[str, Any] = {
    "level": 90,
    "stats": [
        {"key": "atk", "value": 2000},
        {"key": "crit_rate", "value": 0.5},
        {"key": "crit_dmg", "value": 1.0},
        {"key": "pyro_dmg", "value": 0.466},
        {"key": "elemental_mastery", "value": 200},
    ],
    "scalings": [{"stat": "atk", "multiplier": 1.0}],
    "bonus": None,
    "reaction": "none",
    "enemy_level": 90,
    "enemy_resistance": 0.1,
}


def test_returns_non_crit_crit_and_average() -> None:
    response = client.post(URL, json=VALID)
    assert response.status_code == 200
    assert response.json() == pytest.approx({"non_crit": 900, "crit": 1800, "average": 1350})


def test_uses_the_bonus_and_reaction_asked_for() -> None:
    body = client.post(URL, json={**VALID, "bonus": "pyro_dmg", "reaction": "strong"}).json()
    assert body["non_crit"] == pytest.approx(900 * 1.466 * 2 * 1.3475)


@pytest.mark.parametrize(
    "override",
    [
        {"level": 0},
        {"level": 101},
        {"scalings": []},
        {"scalings": [{"stat": "atk", "multiplier": 0}]},
        {"scalings": [{"stat": "atk", "multiplier": -1}]},
        {"scalings": [{"stat": "atk", "multiplier": 101}]},
        {"scalings": [{"stat": "crit_rate", "multiplier": 1}]},
        {"scalings": [{"stat": "atk", "multiplier": 1}] * 5},
        {"flat": -1},
        {"flat": 1e12},
        {"def_reduction": -0.1},
        {"def_reduction": 1.1},
        {"def_ignore": 1.1},
        {"res_reduction": -0.1},
        {"res_reduction": 10.1},
        {"bonus": "atk"},
        {"reaction": "overload"},
        {"enemy_level": 0},
        {"enemy_level": 201},
        {"enemy_resistance": -1.1},
        {"enemy_resistance": 10.1},
        {"stats": [{"key": "luck", "value": 1}]},
        {"stats": [{"key": "atk", "value": -1e12}]},
        {"stats": [{"key": "atk", "value": 1e12}]},
        {"stats": [{"key": "atk", "value": 1}] * 31},
    ],
    ids=lambda override: f"{next(iter(override))}={str(next(iter(override.values())))[:24]}",
)
def test_rejects_input_outside_the_game(override: dict[str, Any]) -> None:
    assert client.post(URL, json={**VALID, **override}).status_code == 422


def test_accepts_a_negative_crit_rate() -> None:
    # Kokomi's passive takes 100% off her CRIT Rate.
    stats = [{"key": "atk", "value": 2000}, {"key": "crit_rate", "value": -0.95}]
    response = client.post(URL, json={**VALID, "stats": stats})
    assert response.status_code == 200
    assert response.json()["average"] == pytest.approx(900)


def test_rejects_numbers_that_are_not_finite() -> None:
    body = '{"level": 90, "stats": [], "scalings": [{"stat": "atk", "multiplier": NaN}], '
    body += '"bonus": null, "reaction": "none", "enemy_level": 90, "enemy_resistance": 0.1}'
    response = client.post(URL, content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "scalings", 0, "multiplier"]


def test_adds_the_stats_a_hit_scales_with() -> None:
    scalings = [{"stat": "atk", "multiplier": 1.0}, {"stat": "elemental_mastery", "multiplier": 2}]
    body = client.post(URL, json={**VALID, "scalings": scalings}).json()
    assert body["non_crit"] == pytest.approx((2000 + 400) * 0.45)


def test_uses_flat_damage_and_what_the_team_takes_off_the_enemy() -> None:
    extra = {"flat": 1000, "def_reduction": 0.3, "def_ignore": 0.0, "res_reduction": 0.4}
    body = client.post(URL, json={**VALID, **extra}).json()
    # 3000 base, defense 190 / (190 + 133), resistance 10% - 40% = -30%, worth +15%
    assert body["non_crit"] == pytest.approx(3000 * 190 / 323 * 1.15)


def test_takes_aggravate_and_spread() -> None:
    for reaction in ("aggravate", "spread"):
        response = client.post(URL, json={**VALID, "reaction": reaction})
        assert response.status_code == 200
        assert response.json()["non_crit"] > 900
