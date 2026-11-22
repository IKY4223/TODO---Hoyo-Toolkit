"""The stats a character would have with another artifact in one slot.

shortcut: only the stats a set's 2-piece effect always gives are recounted when a swap breaks or
completes a set; conditional effects and 4-piece effects are not (they depend on the battle). The
values are the ones Enka shows, rounded as the game prints them (46.6% for 46.62%).
"""

from collections import Counter
from collections.abc import Iterable, Mapping

from app.showcase.gamedata import GAMEDATA
from app.showcase.models import Stat, StatKey

# A percent bonus grows the stat it names, from the base value.
PERCENT_OF = {
    StatKey.HP_PERCENT: StatKey.HP,
    StatKey.ATK_PERCENT: StatKey.ATK,
    StatKey.DEF_PERCENT: StatKey.DEF,
}
# Every set with a stat bonus gives it at 2 pieces (the game's tables, November 2026); the 1-piece
# sets give none.
SET_PIECES = 2


def set_change(worn: Iterable[int], old: int | None, new: int) -> list[Stat]:
    """The set bonuses lost (negative) and gained when a piece of set `old` gives way to `new`.

    `worn` holds the set of each artifact worn now; `old` is None for an empty slot.
    """
    before = Counter(worn)
    after = before.copy()
    if old is not None:
        after[old] -= 1
    after[new] += 1
    change: list[Stat] = []
    for set_id in sorted({*before, *after}):
        had, has = before[set_id] >= SET_PIECES, after[set_id] >= SET_PIECES
        if had != has:
            sign = 1 if has else -1
            bonus = GAMEDATA.set_bonuses.get(str(set_id), {})
            change.extend(Stat(key, sign * value) for key, value in bonus.items())
    return change


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
