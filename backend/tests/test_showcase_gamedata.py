"""The talent tables the sync writes, as the app reads them."""

import json
from pathlib import Path

import pytest

from app.damage.levels import LEVEL_MULTIPLIERS
from app.showcase.gamedata import GAMEDATA, TALENTS
from app.showcase.models import StatKey, WeaponType

TALENT_LEVELS = 15  # 10, plus up to 3 from constellations, plus the game's spare rows


def test_a_talent_holds_each_hit_at_every_level() -> None:
    # Kamisato Ayaka's Normal Attack (group 231): her 1-Hit DMG is 45.7% ATK at level 1.
    first = TALENTS["231"][0]
    assert (first.name.en, first.name.ru) == ("1-Hit DMG", "Урон атаки 1")
    assert [term.stat for term in first.terms] == [StatKey.ATK]
    assert first.terms[0].values[0] == pytest.approx(0.457253)
    assert len(first.terms[0].values) == TALENT_LEVELS


def test_nearly_every_character_has_talent_tables() -> None:
    # The game's tables lag Enka's store by a version: the newest few characters wait for them.
    groups = {group for data in GAMEDATA.characters.values() for _, group in data.talents}
    missing = groups - {int(group) for group in TALENTS}
    assert len(missing) <= len(groups) // 10
    assert TALENTS.keys() <= {str(group) for group in groups}


def test_each_character_knows_its_weapon_type() -> None:
    # Lisa (10000006) fights with a catalyst, Amber (10000021) with a bow.
    assert GAMEDATA.characters["10000006"].weapon_type == WeaponType.CATALYST
    assert GAMEDATA.characters["10000021"].weapon_type == WeaponType.BOW


def test_the_file_is_what_the_sync_writes() -> None:
    raw = json.loads((Path(__file__).parents[1] / "app/showcase/talents.json").read_text())
    assert len(raw) == len(TALENTS)


def test_reaction_base_at_level_90() -> None:
    # The level multiplier Aggravate and Spread start from at character level 90.
    assert LEVEL_MULTIPLIERS[90] == pytest.approx(1446.8535, abs=0.001)
    assert 1 in LEVEL_MULTIPLIERS
