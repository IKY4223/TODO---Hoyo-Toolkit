"""The stats a character would have with another artifact in one slot.

shortcut: set bonuses are not recounted, though a swap can break or complete a set, and the
values are the ones Enka shows, rounded as the game prints them (46.6% for 46.62%); add set
effects with the rest of the set data.
"""

from collections.abc import Iterable, Mapping

from app.showcase.models import Stat, StatKey

# A percent bonus grows the stat it names, from the base value.
PERCENT_OF = {
    StatKey.HP_PERCENT: StatKey.HP,
    StatKey.ATK_PERCENT: StatKey.ATK,
    StatKey.DEF_PERCENT: StatKey.DEF,
}


def swap(
    stats: Mapping[StatKey, float],
    base: Mapping[StatKey, float],
    old: Iterable[Stat],
    new: Iterable[Stat],
) -> dict[StatKey, float]:
    """Final stats with the artifact `old` (main stat and substats) taken off and `new` put on."""
    result = dict(stats)
    for sign, artifact in ((-1, old), (1, new)):
        for stat in artifact:
            key = PERCENT_OF.get(stat.key, stat.key)
            value = stat.value * base.get(key, 0.0) if stat.key in PERCENT_OF else stat.value
            result[key] = result.get(key, 0.0) + sign * value
    return result
