"""A player's character showcase, in the shape the rest of the app works with."""

from dataclasses import dataclass
from enum import StrEnum


class WeaponType(StrEnum):
    SWORD = "sword"
    CLAYMORE = "claymore"
    POLEARM = "polearm"
    CATALYST = "catalyst"
    BOW = "bow"


class Element(StrEnum):
    PYRO = "pyro"
    HYDRO = "hydro"
    ELECTRO = "electro"
    CRYO = "cryo"
    ANEMO = "anemo"
    GEO = "geo"
    DENDRO = "dendro"


class Slot(StrEnum):
    FLOWER = "flower"
    PLUME = "plume"
    SANDS = "sands"
    GOBLET = "goblet"
    CIRCLET = "circlet"


class StatKey(StrEnum):
    HP = "hp"
    HP_PERCENT = "hp_percent"
    ATK = "atk"
    ATK_PERCENT = "atk_percent"
    DEF = "def"
    DEF_PERCENT = "def_percent"
    ELEMENTAL_MASTERY = "elemental_mastery"
    ENERGY_RECHARGE = "energy_recharge"
    CRIT_RATE = "crit_rate"
    CRIT_DMG = "crit_dmg"
    HEALING_BONUS = "healing_bonus"
    PHYSICAL_DMG = "physical_dmg"
    PYRO_DMG = "pyro_dmg"
    HYDRO_DMG = "hydro_dmg"
    ELECTRO_DMG = "electro_dmg"
    CRYO_DMG = "cryo_dmg"
    ANEMO_DMG = "anemo_dmg"
    GEO_DMG = "geo_dmg"
    DENDRO_DMG = "dendro_dmg"


@dataclass(frozen=True)
class Stat:
    key: StatKey
    value: float  # every stat except flat HP, ATK, DEF and EM is a fraction: 0.466 is 46.6%


@dataclass(frozen=True)
class Weapon:
    name: str
    rarity: int
    level: int
    refinement: int  # 1 to 5
    icon: str | None  # image URL


@dataclass(frozen=True)
class Artifact:
    slot: Slot
    set_id: int  # the game's id; GameData names it and gives its 2-piece stat bonus
    set_name: str
    rarity: int
    level: int  # 0 to 20
    main: Stat
    subs: tuple[Stat, ...]
    icon: str | None


@dataclass(frozen=True)
class Scaling:
    stat: StatKey  # ATK, HP, DEF or Elemental Mastery
    multiplier: float  # 0.457 is 45.7% of the stat


@dataclass(frozen=True)
class Attack:
    talent: int  # 0 Normal Attack, 1 Elemental Skill, 2 Elemental Burst
    name: str
    name_ru: str
    scalings: tuple[Scaling, ...]  # at the character's talent level, repeated hits included


@dataclass(frozen=True)
class Character:
    id: int  # the game's own id, stable across renames and languages
    name: str
    element: Element | None  # unknown for the elementless Traveler and for too-new characters
    weapon_type: WeaponType | None  # unknown for too-new characters
    level: int
    constellation: int
    talents: tuple[int, ...]  # normal attack, skill, burst, with constellation boosts
    stats: tuple[Stat, ...]  # final values as shown in game
    base_stats: tuple[Stat, ...]  # HP, ATK and DEF before any bonus: character and weapon
    weapon: Weapon
    artifacts: tuple[Artifact, ...]
    icon: str | None
    attacks: tuple[Attack, ...]  # each hit of the three talents the game's tables list


@dataclass(frozen=True)
class Showcase:
    uid: str
    nickname: str
    adventure_rank: int
    characters: tuple[Character, ...]
