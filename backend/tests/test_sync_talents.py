"""How the game data sync reads a line of a talent's table into hits with their multipliers."""

import pytest

from scripts.sync_gamedata import TIMES, level_multipliers, talent_rows

# Two levels of a talent's parameters, enough to see each one is read per level.
LEVELS = [[0.4, 0.5, 0.6, 2.0], [0.8, 1.0, 1.2, 3.0]]


def _row(name: str, *terms: tuple[str, list[float]]) -> dict[str, object]:
    return {
        "name": {"en": name, "ru": name},
        "terms": [{"stat": stat, "values": values} for stat, values in terms],
    }


def test_a_percent_of_attack() -> None:
    rows = talent_rows("1-Hit DMG", "Урон атаки 1", "{param1:F1P}", LEVELS)
    assert rows == [
        {
            "name": {"en": "1-Hit DMG", "ru": "Урон атаки 1"},
            "terms": [{"stat": "atk", "values": [0.4, 0.8]}],
        }
    ]


@pytest.mark.parametrize(
    "fmt", ["{param2:F1P}" + TIMES + "3", "{param2:F1P}*3", "{param2:F2P} ATK " + TIMES + "3"]
)
def test_repeated_hits_count_in_the_multiplier_and_the_name(fmt: str) -> None:
    rows = talent_rows("4-Hit DMG", "4-Hit DMG", fmt, LEVELS)
    assert rows == [_row(f"4-Hit DMG {TIMES}3", ("atk", [1.5, 3.0]))]


def test_a_repeat_belongs_to_the_alternative_it_follows() -> None:
    # Clorinde's Impale the Night: only the third of three hits is dealt three times.
    rows = talent_rows(
        "Impale DMG", "Impale DMG", "{param1:F1P}/{param2:F1P}/{param3:F1P}" + TIMES + "3", LEVELS
    )
    assert rows == [
        _row("Impale DMG (1/3)", ("atk", [0.4, 0.8])),
        _row("Impale DMG (2/3)", ("atk", [0.5, 1.0])),
        _row(f"Impale DMG {TIMES}3 (3/3)", ("atk", [1.8, 3.6])),
    ]


def test_each_part_can_repeat_on_its_own() -> None:
    # Azure Devour: two parts, each dealt twice.
    fmt = "{param1:F1P}" + TIMES + "2+{param2:F1P}" + TIMES + "2"
    rows = talent_rows("Azure Devour DMG", "Azure Devour DMG", fmt, LEVELS)
    assert rows == [_row(f"Azure Devour DMG {TIMES}2", ("atk", [1.8, 3.6]))]


@pytest.mark.parametrize(
    ("fmt", "value"), [("{param1:F1P} per Paw", 0.4), ("{param2:F1P} each", 0.5)]
)
def test_a_hit_counted_per_piece_is_one_piece(fmt: str, value: float) -> None:
    # Diona's Icy Paw DMG per paw, Tighnari's Fatal Blossom DMG each.
    assert talent_rows("Icy Paw DMG", "Icy Paw DMG", fmt, LEVELS) == [
        _row("Icy Paw DMG", ("atk", [value, value * 2]))
    ]


def test_parts_of_one_hit_add_up() -> None:
    rows = talent_rows(
        "Charged Attack DMG", "Charged Attack DMG", "{param1:F1P}+{param2:F1P}", LEVELS
    )
    assert rows == [_row("Charged Attack DMG", ("atk", [0.9, 1.8]))]


def test_alternatives_become_hits_of_their_own() -> None:
    rows = talent_rows(
        "Low/High Plunge DMG", "Low/High Plunge DMG", "{param1:P}/{param2:P}", LEVELS
    )
    assert rows == [
        _row("Low/High Plunge DMG (1/2)", ("atk", [0.4, 0.8])),
        _row("Low/High Plunge DMG (2/2)", ("atk", [0.5, 1.0])),
    ]


def test_each_part_scales_with_its_own_stat() -> None:
    rows = talent_rows(
        "Tri-Karma Purification DMG",
        "Tri-Karma Purification DMG",
        "{param1:F1P} ATK+{param2:F1P} Elemental Mastery",
        LEVELS,
    )
    assert rows == [
        _row(
            "Tri-Karma Purification DMG",
            ("atk", [0.4, 0.8]),
            ("elemental_mastery", [0.5, 1.0]),
        )
    ]


@pytest.mark.parametrize(
    ("fmt", "stat"),
    [
        ("{param1:F1P}+{param2:F1P} DEF", "def"),
        ("{param1:F2P}/{param2:F2P} Max HP", "hp"),
    ],
)
def test_a_stat_named_once_at_the_end_applies_to_every_part(fmt: str, stat: str) -> None:
    rows = talent_rows("Skill DMG", "Skill DMG", fmt, LEVELS)
    assert [term["stat"] for row in rows for term in row["terms"]] == [stat] * (
        1 if "+" in fmt else 2
    )


def test_a_bracketed_sum_repeats_as_a_whole() -> None:
    rows = talent_rows(
        "2-Mirror Projection Attack DMG",
        "2-Mirror Projection Attack DMG",
        "({param1:F1P} ATK+{param2:F1P} Elemental Mastery)" + TIMES + "2",
        LEVELS,
    )
    assert rows == [
        _row(
            f"2-Mirror Projection Attack DMG {TIMES}2",
            ("atk", [0.8, 1.6]),
            ("elemental_mastery", [1.0, 2.0]),
        )
    ]


@pytest.mark.parametrize(
    ("name", "shown"),
    [
        ("#{LAYOUT_MOBILE#Tap}{LAYOUT_PC#Press}{LAYOUT_PS#Press} DMG", "Press DMG"),
        ("#Photo DMG ({LAYOUT_MOBILE#Tap}{LAYOUT_PC#Press}{LAYOUT_PS#Press})", "Photo DMG (Press)"),
    ],
)
def test_the_computer_wording_replaces_the_layout_choice(name: str, shown: str) -> None:
    rows = talent_rows(name, "<color=#FFD780FF>Урон</color>", "{param1:F1P}", LEVELS)
    assert rows[0]["name"] == {"en": shown, "ru": "Урон"}


@pytest.mark.parametrize(
    ("name", "fmt"),
    [
        ("CD", "{param1:F1}s"),  # seconds
        ("Energy Cost", "{param1:I}"),
        ("Healing", "{param1:F1P} ATK+{param2:I}"),  # a flat part: healing or a shield
        ("Activation Cost", "{param1:P} Current HP"),  # not one of the stats a hit scales with
        ("ATK Bonus", "{param1:F1P} DEF"),  # a buff, though written like a hit
        ("Suffusion DMG Bonus", "{param1:F2P} Max HP"),
        ("Bloom DMG Increase", "{param1:F1P} Elemental Mastery"),
        ("Shield DMG Absorption", "{param1:F1P} Max HP"),
        ("Redmane's Blood Maximum", "{param1:P} Max HP"),
        ("Soul Companion DMG", "{param1:F1P} Normal Attack DMG"),  # a share of another hit
        ("Shattering Pressure DMG", "{param1:F1P} Cryo + {param2:F1P} Physical"),
        ("Energy Recharge Bonus", "{param1:P} per Electro Sigil"),
        ("Bond of Life Gain", "{param1:P} Max HP"),
        ("Mitigation", "{param1:P} ATK"),
        # Lunar reactions follow a formula of their own (see app/damage/engine.py).
        ("Gravity Interference: Lunar-Charged DMG", "{param1:F1P} ATK"),
        ("Gentilhomme Usher HP Consumption", "{param1:F1P} Current HP"),
        ("Inherited HP", "{param1:P}"),
        ("High Nightsoul Points ATK Conversion Rate", "{param1:F1P}"),
    ],
)
def test_lines_that_are_not_one_hit_are_left_out(name: str, fmt: str) -> None:
    assert talent_rows(name, name, fmt, LEVELS) == []


def test_a_name_missing_in_russian_falls_back_to_english() -> None:
    rows = talent_rows("Skill DMG", "", "{param1:P}", LEVELS)
    assert rows[0]["name"] == {"en": "Skill DMG", "ru": "Skill DMG"}


def test_level_multipliers_come_per_character_level() -> None:
    table = [
        {"level": 1, "playerElementLevelCo": 17.17, "elementLevelCo": 1},
        {"level": 90, "playerElementLevelCo": 1446.8535, "elementLevelCo": 2},
    ]
    assert level_multipliers(table) == {"1": 17.17, "90": 1446.8535}
