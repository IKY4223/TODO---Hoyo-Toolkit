"""Rebuild the Genshin game data the app ships with.

app/showcase/gamedata.json comes from the Enka.Network data store; app/showcase/talents.json and
app/damage/levels.json come from the game's own tables as Dimbreath/AnimeGameData publishes them
(ProudSkillExcelConfigData, ElementCoeffExcelConfigData and the text maps). That repository
states no licence: it holds the game's data, which belongs to HoYoverse.

Run after each game version: uv run python scripts/sync_gamedata.py
"""

import json
import re
from pathlib import Path
from typing import Any
from urllib.request import urlopen

STORE = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/gi/"
GAME_DATA = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/"
APP = Path(__file__).parent.parent / "app"
TARGET = APP / "showcase" / "gamedata.json"
TALENTS = APP / "showcase" / "talents.json"
LEVELS = APP / "damage" / "levels.json"
# The talent tables' labels live in both the short and the medium text maps; Russian is split
# in two files of each.
TEXT_MAPS = {
    "en": ["TextMapEN.json", "TextMap_MediumEN.json"],
    "ru": [
        "TextMapRU_0.json",
        "TextMapRU_1.json",
        "TextMap_MediumRU_0.json",
        "TextMap_MediumRU_1.json",
    ],
}

# The stats a talent's line names after a percentage, as the API keys them.
SCALINGS = {"ATK": "atk", "Max HP": "hp", "DEF": "def", "Elemental Mastery": "elemental_mastery"}
# Lines written like a hit that are buffs, shields, heals or limits instead.
# shortcut: told apart by words of the English name, so a new kind of line can slip through;
# read the list of names the sync prints after each game version.
NOT_A_HIT = (
    "Bonus",
    "Increase",
    "Decrease",
    "Reduction",
    "Absorption",
    "Maximum",
    "Cost",
    "Healing",
    "Regeneration",
    "Consumption",
    "Inherited",
    "Conversion",
)
# One part of a hit: a percentage parameter, perhaps followed by the stat it is a percent of.
# Accepts "{param1:F1P}" and "{param2:P} Max HP"; rejects "{param1:F1}s" and "{param1:I}".
# https://regex101.com/?flavor=python&regex=%5C%7Bparam%28%5Cd%2B%29%3A%28%3F%3AF%5Cd%29%3FP%5C%7D%5Cs*%28ATK%7CMax+HP%7CDEF%7CElemental+Mastery%29%3F&testString=%7Bparam2%3AP%7D+Max+HP
PART = re.compile(r"\{param(\d+):(?:F\d)?P\}\s*(ATK|Max HP|DEF|Elemental Mastery)?")
TIMES = "\u00d7"  # the multiplication sign the game writes a repeated hit with
# A hit repeated: "{param4:F1P}" TIMES "3", "{param1:F1P}*4", "({param1:F1P} ATK+...)" TIMES "2".
REPEAT = re.compile(rf"\(?(.*?)\)?\s*[{TIMES}*]\s*(\d+)")
# The game words a line for each device; the site shows the computer's wording. A leading "#"
# only marks a line that holds such markup.
LAYOUT = re.compile(r"#?\{LAYOUT_MOBILE#[^}]*\}\{LAYOUT_PC#([^}]*)\}\{LAYOUT_PS#[^}]*\}")
TAG = re.compile(r"<[^>]+>")

ELEMENTS = {
    "Fire": "pyro",
    "Water": "hydro",
    "Electric": "electro",
    "Ice": "cryo",
    "Wind": "anemo",
    "Rock": "geo",
    "Grass": "dendro",
    "None": None,  # the Traveler before resonating with an element
}


def load(name: str, base: str = STORE) -> Any:
    # S310: every base is a constant https address.
    with urlopen(base + name, timeout=300) as response:  # noqa: S310
        return json.load(response)


def _clean(name: str) -> str:
    return TAG.sub("", LAYOUT.sub(r"\1", name)).lstrip("#").strip()


def talent_rows(
    name_en: str, name_ru: str, fmt: str, levels: list[list[float]]
) -> list[dict[str, Any]]:
    """The hits one line of a talent's table describes, with their multiplier at each level.

    `fmt` is the line's value as the game writes it, such as "{param1:F1P}+{param2:F1P}";
    `levels` holds the talent's parameters at each level. A line that is not one hit gives none.
    """
    if any(word in name_en for word in NOT_A_HIT):
        return []
    body, hits = fmt.strip(), 1
    if repeat := REPEAT.fullmatch(body):
        body, hits = repeat[1], int(repeat[2])
    parsed: list[list[tuple[int, str | None]]] = []
    for text in body.split("/"):
        parts = [PART.fullmatch(part.strip()) for part in text.split("+")]
        if not all(parts):
            return []
        parsed.append([(int(part[1]), part[2]) for part in parts if part])
    # "{param1:F1P}+{param2:F1P} DEF": a stat named once at the end is every bare part's stat.
    named: str | None = None
    stats: list[str] = []
    for _, stat in reversed([part for alternative in parsed for part in alternative]):
        named = stat or named
        stats.insert(0, named or "ATK")
    alternatives: list[list[tuple[int, str]]] = []
    for written in parsed:
        alternatives.append([(param, stats.pop(0)) for param, _ in written])
    if max(param for alternative in alternatives for param, _ in alternative) > len(levels[0]):
        return []
    en, ru = _clean(name_en), _clean(name_ru) or _clean(name_en)
    suffix = f" {TIMES}{hits}" if hits > 1 else ""
    rows = []
    for number, alternative in enumerate(alternatives, 1):
        which = f" ({number}/{len(alternatives)})" if len(alternatives) > 1 else ""
        terms: dict[str, list[float]] = {}
        for param, part_stat in alternative:
            key = SCALINGS[part_stat]
            values = [hits * level[param - 1] for level in levels]
            before = terms.get(key, [0.0] * len(levels))
            terms[key] = [a + b for a, b in zip(before, values, strict=True)]
        rows.append(
            {
                "name": {"en": en + suffix + which, "ru": ru + suffix + which},
                "terms": [
                    {"stat": key, "values": [round(value, 6) for value in values]}
                    for key, values in terms.items()
                ],
            }
        )
    return rows


def level_multipliers(table: list[dict[str, Any]]) -> dict[str, float]:
    """The base of Aggravate and Spread at each character level."""
    return {str(row["level"]): row["playerElementLevelCo"] for row in table}


def _text(language: str) -> dict[str, str]:
    text: dict[str, str] = {}
    for name in TEXT_MAPS[language]:
        text.update(load("TextMap/" + name, GAME_DATA))
    return text


def talents(groups: set[int]) -> dict[str, list[dict[str, Any]]]:
    """Each talent level group's hits, keyed by the group id gamedata.json lists."""
    by_group: dict[int, dict[int, dict[str, Any]]] = {}
    for row in load("ExcelBinOutput/ProudSkillExcelConfigData.json", GAME_DATA):
        if row["proudSkillGroupId"] in groups:
            by_group.setdefault(row["proudSkillGroupId"], {})[row["level"]] = row
    en, ru = _text("en"), _text("ru")
    result = {}
    for group, by_level in sorted(by_group.items()):
        levels = [by_level[level]["paramList"] for level in sorted(by_level)]
        rows = []
        for label in by_level[min(by_level)]["paramDescList"]:
            name_en, _, fmt = en.get(str(label), "").partition("|")
            name_ru = ru.get(str(label), "").partition("|")[0]
            rows.extend(talent_rows(name_en, name_ru, fmt, levels) if fmt else [])
        result[str(group)] = rows
    return result


def main() -> None:
    names = load("locs.json")["en"]
    gamedata = {
        "characters": {
            key: {
                "name": names[str(avatar["NameTextMapHash"])],
                "element": ELEMENTS[avatar["Element"]],
                # SideIconName is "/ui/UI_AvatarIcon_Side_Ambor.png"; the portrait has no "Side_".
                "icon": avatar["SideIconName"]
                .removeprefix("/ui/")
                .removesuffix(".png")
                .replace("Side_", ""),
                # Talent ids in display order, each with the id constellations boost it by.
                "talents": [
                    [skill, avatar["ProudMap"][str(skill)]] for skill in avatar["SkillOrder"]
                ],
            }
            for key, avatar in load("avatars.json").items()
        },
        "weapons": {
            key: names[str(weapon["NameTextMapHash"])]
            for key, weapon in load("weapons.json").items()
        },
        "sets": {
            key: names[relic_set["Name"]] for key, relic_set in load("relics.json")["Sets"].items()
        },
    }
    TARGET.write_text(json.dumps(gamedata, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    print({kind: len(entries) for kind, entries in gamedata.items()})
    groups = {group for avatar in gamedata["characters"].values() for _, group in avatar["talents"]}
    hits = talents(groups)
    TALENTS.write_text(json.dumps(hits, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"talents: {len(hits)} of {len(groups)} groups")
    print(sorted({row["name"]["en"] for rows in hits.values() for row in rows}))
    coefficients = load("ExcelBinOutput/ElementCoeffExcelConfigData.json", GAME_DATA)
    LEVELS.write_text(json.dumps(level_multipliers(coefficients), indent=1) + "\n")


if __name__ == "__main__":
    main()
