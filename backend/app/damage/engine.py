"""Outgoing damage of one hit.

The game does not publish its damage formula. This is the community one, verified by player
testing: KQM Theorycrafting Library, "Damage Formula",
https://library.keqingmains.com/combat-mechanics/damage/damage-formula (read November 2026), and
its "Transformative Reactions" page (read 18 November 2026) for Overloaded, Bloom and the rest.

shortcut: Lunar reactions (6.0 and later) are not modelled: neither page gives their formula.
Electro-Charged is counted as one tick; a transformative reaction's resistance is taken as the
hit's; one reaction bonus serves both reactions of a hit, though sets give each its own (Thundering
Fury: 20% to Aggravate, 40% to Hyperbloom). Add each when a source or a feature needs it.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from app.damage.levels import LEVEL_MULTIPLIERS
from app.showcase.models import Scaling, StatKey


class Reaction(StrEnum):
    NONE = "none"
    WEAK = "weak"  # x1.5: Pyro on Hydro (Vaporize), Cryo on Pyro (Melt)
    STRONG = "strong"  # x2: Hydro on Pyro (Vaporize), Pyro on Cryo (Melt)
    AGGRAVATE = "aggravate"  # Electro on Quicken: adds to the hit's base damage
    SPREAD = "spread"  # Dendro on Quicken: adds to the hit's base damage


class Transformative(StrEnum):
    """A reaction that deals damage of its own, beside the hit that set it off."""

    BURNING = "burning"
    SUPERCONDUCT = "superconduct"
    SWIRL = "swirl"
    ELECTRO_CHARGED = "electro_charged"
    SHATTERED = "shattered"
    OVERLOADED = "overloaded"
    BLOOM = "bloom"
    HYPERBLOOM = "hyperbloom"
    BURGEON = "burgeon"


@dataclass(frozen=True)
class Hit:
    scalings: tuple[Scaling, ...]  # the stats the talent multiplies: 3.92 for 392%
    bonus: StatKey | None  # the damage bonus that applies, such as pyro_dmg
    reaction: Reaction
    flat: float = 0.0  # damage added to the base: Shenhe's quills, Yun Jin's burst
    transformative: Transformative | None = None  # a reaction the hit also sets off
    reaction_bonus: float = 0.0  # Crimson Witch, Thundering Fury: 0.4 for 40%


@dataclass(frozen=True)
class Enemy:
    level: int
    resistance: float  # to the hit's damage type: 0.1 for 10%
    def_reduction: float = 0.0  # Lisa's passive, Klee's C2: 0.23 for 23%
    def_ignore: float = 0.0  # Raiden's C2, Yae Miko's C6
    res_reduction: float = 0.0  # Superconduct, Viridescent Venerer: 0.4 for 40%


@dataclass(frozen=True)
class Damage:
    non_crit: float
    crit: float
    average: float  # over many hits at the character's CRIT Rate
    reaction: float = 0.0  # the transformative reaction's own damage; it cannot crit


AMPLIFYING = {Reaction.WEAK: 1.5, Reaction.STRONG: 2.0}
ADDITIVE = {Reaction.AGGRAVATE: 1.15, Reaction.SPREAD: 1.25}
# The formula page's reaction multipliers; Electro-Charged's is per tick.
TRANSFORMATIVE = {
    Transformative.BURNING: 0.25,
    Transformative.SUPERCONDUCT: 1.5,
    Transformative.SWIRL: 0.6,
    Transformative.ELECTRO_CHARGED: 2.0,
    Transformative.SHATTERED: 3.0,
    Transformative.OVERLOADED: 2.75,
    Transformative.BLOOM: 2.0,
    Transformative.HYPERBLOOM: 3.0,
    Transformative.BURGEON: 3.0,
}
# Resistance at or above this is divided down instead of subtracted.
HIGH_RESISTANCE = 0.75
MAX_DEF_REDUCTION = 0.9  # the formula page: "DefReduction is hard capped at 90%"


def _defense_factor(level: int, enemy: Enemy) -> float:
    reduction = min(enemy.def_reduction, MAX_DEF_REDUCTION)
    own = level + 100
    return own / (own + (enemy.level + 100) * (1 - reduction) * (1 - enemy.def_ignore))


def _resistance_factor(enemy: Enemy) -> float:
    resistance = enemy.resistance - enemy.res_reduction
    if resistance < 0:
        return 1 - resistance / 2  # negative resistance is worth half
    if resistance < HIGH_RESISTANCE:
        return 1 - resistance
    return 1 / (4 * resistance + 1)


def _amplifying_factor(reaction: Reaction, mastery: float, bonus: float) -> float:
    if reaction not in AMPLIFYING:
        return 1.0
    return AMPLIFYING[reaction] * (1 + 2.78 * mastery / (mastery + 1400) + bonus)


def _additive(reaction: Reaction, level: int, mastery: float, bonus: float) -> float:
    if reaction not in ADDITIVE:
        return 0.0
    return (
        ADDITIVE[reaction] * LEVEL_MULTIPLIERS[level] * (1 + 5 * mastery / (mastery + 1200) + bonus)
    )


def _transformative(hit: Hit, level: int, mastery: float, enemy: Enemy) -> float:
    """Neither the enemy's defense nor the hit's own numbers count; resistance does."""
    if hit.transformative is None:
        return 0.0
    return (
        TRANSFORMATIVE[hit.transformative]
        * LEVEL_MULTIPLIERS[level]
        * (1 + 16 * mastery / (mastery + 2000) + hit.reaction_bonus)
        * _resistance_factor(enemy)
    )


def damage(level: int, stats: Mapping[StatKey, float], hit: Hit, enemy: Enemy) -> Damage:
    """Damage one hit deals. `stats` are the character's final values; a missing stat is 0."""
    bonus = stats.get(hit.bonus, 0.0) if hit.bonus else 0.0
    mastery = stats.get(StatKey.ELEMENTAL_MASTERY, 0.0)
    base = (
        sum(stats.get(scaling.stat, 0.0) * scaling.multiplier for scaling in hit.scalings)
        + hit.flat
        + _additive(hit.reaction, level, mastery, hit.reaction_bonus)
    )
    non_crit = (
        base
        * (1 + bonus)
        * _amplifying_factor(hit.reaction, mastery, hit.reaction_bonus)
        * _defense_factor(level, enemy)
        * _resistance_factor(enemy)
    )
    crit_dmg = stats.get(StatKey.CRIT_DMG, 0.0)
    crit_rate = min(1.0, max(0.0, stats.get(StatKey.CRIT_RATE, 0.0)))
    return Damage(
        non_crit=non_crit,
        crit=non_crit * (1 + crit_dmg),
        average=non_crit * (1 + crit_rate * crit_dmg),
        reaction=_transformative(hit, level, mastery, enemy),
    )
