from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator

from app.damage.artifacts import set_change, swap
from app.damage.engine import Damage, Enemy, Hit, Reaction, Transformative, damage
from app.ratelimit import RateLimiter, limited
from app.showcase.models import Scaling, Slot, Stat, StatKey

ScalingStat = Literal[StatKey.ATK, StatKey.HP, StatKey.DEF, StatKey.ELEMENTAL_MASTERY]
DamageBonus = Literal[
    StatKey.PHYSICAL_DMG,
    StatKey.PYRO_DMG,
    StatKey.HYDRO_DMG,
    StatKey.ELECTRO_DMG,
    StatKey.CRYO_DMG,
    StatKey.ANEMO_DMG,
    StatKey.GEO_DMG,
    StatKey.DENDRO_DMG,
]

# Generous bounds: they keep nonsense out without tracking each game version's caps.
MAX_LEVEL = 100
MAX_ENEMY_LEVEL = 200
MAX_STAT = 1_000_000
MAX_STATS = 30
MAX_MULTIPLIER = 100  # 10 000%
MAX_SCALINGS = 4  # a hit scales with at most two stats in the game's tables
MIN_RESISTANCE = -1
MAX_RESISTANCE = 10
MAX_FLAT = 1_000_000
MAX_SUBSTATS = 4
MAX_CANDIDATES = 60  # every artifact of a full showcase: 12 characters, 5 slots
MAX_SET_ID = 1_000_000  # set ids run to 15 048 today

limiter = RateLimiter(limit=60, window=60)

router = APIRouter(prefix="/api/damage", tags=["damage"], dependencies=[Depends(limited(limiter))])


class StatValue(BaseModel):
    key: StatKey
    # Negative on purpose: Kokomi's CRIT Rate is below zero.
    value: float = Field(ge=-MAX_STAT, le=MAX_STAT, allow_inf_nan=False)


class TalentScaling(BaseModel):
    stat: ScalingStat = Field(description="The stat the talent multiplies")
    multiplier: float = Field(
        gt=0, le=MAX_MULTIPLIER, allow_inf_nan=False, description="Talent multiplier: 3.92 is 392%"
    )


class DamageRequest(BaseModel):
    level: int = Field(ge=1, le=MAX_LEVEL, description="Character level")
    stats: list[StatValue] = Field(max_length=MAX_STATS, description="The character's final stats")
    scalings: list[TalentScaling] = Field(min_length=1, max_length=MAX_SCALINGS)
    bonus: DamageBonus | None = Field(description="The damage bonus that applies to the hit")
    reaction: Reaction
    transformative: Transformative | None = Field(
        default=None, description="A reaction the hit also sets off, which deals its own damage"
    )
    reaction_bonus: float = Field(
        default=0,
        ge=0,
        le=MAX_RESISTANCE,
        allow_inf_nan=False,
        description="Reaction damage bonus, such as Crimson Witch's: 0.15 is 15%",
    )
    flat: float = Field(
        default=0, ge=0, le=MAX_FLAT, allow_inf_nan=False, description="Damage added to the base"
    )
    enemy_level: int = Field(ge=1, le=MAX_ENEMY_LEVEL)
    enemy_resistance: float = Field(
        ge=MIN_RESISTANCE, le=MAX_RESISTANCE, allow_inf_nan=False, description="0.1 is 10%"
    )
    # Above 90% the engine counts 90%: the team's sources may add up past the cap.
    def_reduction: float = Field(default=0, ge=0, le=1, allow_inf_nan=False)
    def_ignore: float = Field(default=0, ge=0, le=1, allow_inf_nan=False)
    res_reduction: float = Field(default=0, ge=0, le=MAX_RESISTANCE, allow_inf_nan=False)


BASE_KEYS = (StatKey.HP, StatKey.ATK, StatKey.DEF)


class BaseStat(BaseModel):
    key: Literal[StatKey.HP, StatKey.ATK, StatKey.DEF]
    value: float = Field(ge=0, le=MAX_STAT, allow_inf_nan=False)


class ArtifactStats(BaseModel):
    slot: Slot
    set_id: int = Field(default=0, ge=0, le=MAX_SET_ID, description="0 when unknown: no set bonus")
    main: StatValue
    subs: list[StatValue] = Field(max_length=MAX_SUBSTATS)


class ArtifactRequest(DamageRequest):
    base_stats: list[BaseStat] = Field(
        max_length=3, description="HP, ATK and DEF before any bonus, as the showcase gives them"
    )
    equipped: list[ArtifactStats] = Field(max_length=len(Slot))

    @field_validator("base_stats")
    @classmethod
    def _each_base_once(cls, value: list[BaseStat]) -> list[BaseStat]:
        # Without one, its percent bonuses would count for nothing, silently.
        if sorted(stat.key for stat in value) != sorted(BASE_KEYS):
            raise ValueError("base_stats must give HP, ATK and DEF once each")
        return value

    candidates: list[ArtifactStats] = Field(min_length=1, max_length=MAX_CANDIDATES)


class ArtifactComparison(BaseModel):
    current: Damage
    candidates: list[Damage]  # in the order asked, each with that artifact in its slot


def _hit(request: DamageRequest) -> Hit:
    return Hit(
        scalings=tuple(Scaling(item.stat, item.multiplier) for item in request.scalings),
        bonus=request.bonus,
        reaction=request.reaction,
        flat=request.flat,
        transformative=request.transformative,
        reaction_bonus=request.reaction_bonus,
    )


def _enemy(request: DamageRequest) -> Enemy:
    return Enemy(
        level=request.enemy_level,
        resistance=request.enemy_resistance,
        def_reduction=request.def_reduction,
        def_ignore=request.def_ignore,
        res_reduction=request.res_reduction,
    )


def _stats(artifact: ArtifactStats) -> list[Stat]:
    return [Stat(stat.key, stat.value) for stat in (artifact.main, *artifact.subs)]


@router.post("")
def calculate_damage(request: DamageRequest) -> Damage:
    return damage(
        request.level,
        {stat.key: stat.value for stat in request.stats},
        _hit(request),
        _enemy(request),
    )


@router.post("/artifacts")
def compare_artifacts(request: ArtifactRequest) -> ArtifactComparison:
    """The hit's damage now, and with each candidate in place of the artifact in its slot."""
    stats = {stat.key: stat.value for stat in request.stats}
    base: dict[StatKey, float] = {stat.key: stat.value for stat in request.base_stats}
    # The first artifact given for a slot is the one worn there.
    worn = {artifact.slot: artifact for artifact in reversed(request.equipped)}
    sets = [artifact.set_id for artifact in worn.values()]
    hit, enemy = _hit(request), _enemy(request)

    def put_on(candidate: ArtifactStats) -> dict[StatKey, float]:
        old = worn.get(candidate.slot)
        bonus = set_change(sets, old.set_id if old else None, candidate.set_id)
        return swap(stats, base, _stats(old) if old else [], [*_stats(candidate), *bonus])

    return ArtifactComparison(
        current=damage(request.level, stats, hit, enemy),
        candidates=[
            damage(request.level, put_on(candidate), hit, enemy) for candidate in request.candidates
        ],
    )
