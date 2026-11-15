import { type JSX, type SubmitEvent, useRef, useState } from 'react'
import { isKeyOf } from '../api/http'
import {
  MAX_ARTIFACT_CANDIDATES,
  MAX_ENEMY_LEVEL,
  MAX_FLAT_DAMAGE,
  MAX_MULTIPLIER,
  MAX_RESISTANCE,
  MIN_RESISTANCE,
} from '../api/limits'
import { useRequest } from '../api/useRequest'
import { type Message, useLanguage, useLocalized, useT, numberFormat } from '../i18n'
import {
  type Artifact,
  type Attack,
  type Character,
  formatStat,
  SCALINGS,
  SLOTS,
} from '../showcase/showcase'
import {
  type ArtifactComparison,
  type ArtifactRequest,
  type Candidate,
  type Damage,
  type DamageRequest,
  fetchComparison,
  fetchDamage,
  isBaseStat,
} from './damage'

// `satisfies` makes a choice added to the API a compile error here.
const REACTIONS = {
  none: 'None',
  weak: 'Vaporize / Melt ×1.5',
  strong: 'Vaporize / Melt ×2',
  aggravate: 'Aggravate',
  spread: 'Spread',
} as const satisfies Record<DamageRequest['reaction'], Message>

const BONUSES = {
  physical_dmg: true,
  pyro_dmg: true,
  hydro_dmg: true,
  electro_dmg: true,
  cryo_dmg: true,
  anemo_dmg: true,
  geo_dmg: true,
  dendro_dmg: true,
} as const satisfies Record<NonNullable<DamageRequest['bonus']>, true>

const TALENTS: readonly Message[] = ['Normal Attack', 'Elemental Skill', 'Elemental Burst']

const RESULTS = [
  { label: 'Average', key: 'average' },
  { label: 'Crit', key: 'crit' },
  { label: 'Non-crit', key: 'non_crit' },
] as const satisfies readonly { label: Message; key: keyof Damage }[]

// The second part of a hit that scales with two stats, such as ATK and Elemental Mastery.
const PART_LABELS = [
  { multiplier: 'Talent multiplier, %', scaling: 'Scales with' },
  { multiplier: 'Second part, %', scaling: 'Second part scales with' },
] as const satisfies readonly { multiplier: Message; scaling: Message }[]

const DEFAULT_MULTIPLIER_PERCENT = 100
const DEFAULT_ENEMY_LEVEL = 90
const DEFAULT_RESISTANCE_PERCENT = 10
const PERCENT = 100
const NO_BONUS = ''
const OWN_MULTIPLIER = ''
// A multiplier from the tables is shown to two decimals of a percent, as the game prints it.
const SHOWN_DECIMALS = 100

type Stat = keyof typeof SCALINGS

interface Part {
  readonly stat: Stat
  readonly percent: string
}

const whole = numberFormat({ maximumFractionDigits: 0 })
const relative = numberFormat({
  style: 'percent',
  signDisplay: 'exceptZero',
  maximumFractionDigits: 1,
})
const OWN_PART: readonly Part[] = [{ stat: 'atk', percent: String(DEFAULT_MULTIPLIER_PERCENT) }]

/** The key a <select> holds, or an error if the page was tampered into an impossible choice. */
function choice<TTable extends object>(table: TTable, value: unknown): keyof TTable {
  if (!isKeyOf(table, value)) throw new Error(`Unexpected choice: ${String(value)}`)
  return value
}

// No hit in the game's tables scales with more than two stats.
const partsOf = (attack: Attack): Part[] =>
  attack.scalings
    .filter((scaling) => isKeyOf(SCALINGS, scaling.stat))
    .slice(0, PART_LABELS.length)
    .map((scaling) => ({
      stat: choice(SCALINGS, scaling.stat),
      percent: String(Math.round(scaling.multiplier * PERCENT * SHOWN_DECIMALS) / SHOWN_DECIMALS),
    }))

// shortcut: a Normal Attack is taken as Physical and a skill or burst as the character's element,
// which is wrong for catalysts and infused attacks; the player can change it in the form.
function likelyBonus(attack: Attack, character: Character, offered: readonly string[]): string {
  const physical = attack.talent === 0 || !character.element
  const bonus = physical ? 'physical_dmg' : `${character.element}_dmg`
  return offered.includes(bonus) ? bonus : NO_BONUS
}

function readRequest(data: FormData, character: Character, parts: readonly Part[]): DamageRequest {
  const bonus = data.get('bonus')
  const fraction = (name: string): number => Number(data.get(name)) / PERCENT
  return {
    level: character.level,
    stats: character.stats,
    scalings: parts.map(({ stat, percent }) => ({ stat, multiplier: Number(percent) / PERCENT })),
    bonus: bonus === NO_BONUS ? null : choice(BONUSES, bonus),
    reaction: choice(REACTIONS, data.get('reaction')),
    flat: Number(data.get('flat')),
    enemy_level: Number(data.get('enemy_level')),
    enemy_resistance: fraction('enemy_resistance'),
    def_reduction: fraction('def_reduction'),
    def_ignore: fraction('def_ignore'),
    res_reduction: fraction('res_reduction'),
  }
}

/** A percentage the team takes off the enemy, from 0 up to `max`. */
function Reduction(props: {
  readonly name: string
  readonly label: Message
  readonly max: number
}): JSX.Element {
  const t = useT()
  return (
    <label>
      {t(props.label)}
      <input
        name={props.name}
        type="number"
        inputMode="decimal"
        min={0}
        max={props.max}
        step="any"
        defaultValue={0}
        required
      />
    </label>
  )
}

const statsOf = ({ slot, main, subs }: Artifact): ArtifactRequest['equipped'][number] => ({
  slot,
  main,
  subs,
})

/** The best artifact of each slot others in the showcase wear, against the one worn now. */
function Trials(props: {
  readonly comparison: ArtifactComparison
  readonly tried: readonly Candidate[]
}): JSX.Element {
  const { comparison, tried } = props
  const t = useT()
  const now = comparison.current.average
  const slots = Object.entries(SLOTS).flatMap(([slot, label]) => {
    const own = tried.flatMap((candidate, at) => {
      const damage = comparison.candidates[at]
      return candidate.artifact.slot === slot && damage ? [{ ...candidate, damage }] : []
    })
    const best = own.reduce<(typeof own)[number] | null>(
      (top, next) => (top && top.damage.average >= next.damage.average ? top : next),
      null,
    )
    return best ? [{ slot, label, best }] : []
  })
  return (
    <ul className="trials">
      {slots.map(({ slot, label, best }) => (
        <li key={slot}>
          <strong>{t(label)}</strong>{' '}
          <span>
            {best.damage.average > now
              ? [
                  best.owner,
                  best.artifact.set_name,
                  `${formatStat(best.artifact.main, t)} — ${whole.format(best.damage.average)}`,
                ].join(' · ') + ` (${relative.format(best.damage.average / now - 1)})`
              : t('no artifact here does better')}
          </span>
        </li>
      ))}
    </ul>
  )
}

export function DamageCalculator(props: {
  readonly character: Character
  /** Artifacts the other characters in the showcase wear. */
  readonly others?: readonly Candidate[]
}): JSX.Element {
  const { character, others = [] } = props
  const [state, run] = useRequest<Damage>()
  const [trial, runTrial] = useRequest<ArtifactComparison>()
  const form = useRef<HTMLFormElement>(null)
  // A full showcase has fewer artifacts than the API takes; the cap only guards a changed game.
  const tried = others.slice(0, MAX_ARTIFACT_CANDIDATES)
  const t = useT()
  const language = useLanguage()
  const localized = useLocalized()
  const bonuses = character.stats.filter((stat) => isKeyOf(BONUSES, stat.key))
  const [hit, setHit] = useState(OWN_MULTIPLIER)
  const [parts, setParts] = useState<readonly Part[]>(OWN_PART)
  const [bonus, setBonus] = useState<string>(bonuses[0]?.key ?? NO_BONUS)

  const choose = (value: string): void => {
    setHit(value)
    const attack = character.attacks[Number(value)]
    if (value === OWN_MULTIPLIER || !attack) {
      setParts(OWN_PART)
      return
    }
    setParts(partsOf(attack))
    setBonus(likelyBonus(attack, character, bonuses.map((stat) => stat.key)))
  }

  const change = (index: number, part: Partial<Part>): void => {
    setParts(parts.map((old, at) => (at === index ? { ...old, ...part } : old)))
  }

  const submit = (event: SubmitEvent<HTMLFormElement>): void => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    void run(async () => fetchDamage(readRequest(data, character, parts)))
  }

  const tryArtifacts = (): void => {
    if (!form.current?.reportValidity()) return
    const request = readRequest(new FormData(form.current), character, parts)
    void runTrial(async () =>
      fetchComparison({
        ...request,
        base_stats: character.base_stats.filter(isBaseStat),
        equipped: character.artifacts.map(statsOf),
        candidates: tried.map(({ artifact }) => statsOf(artifact)),
      }),
    )
  }

  return (
    <details>
      <summary>{t('Damage')}</summary>
      <form ref={form} onSubmit={submit}>
        {character.attacks.length ? (
          <label>
            {t('Hit')}
            <select value={hit} onChange={(event) => choose(event.target.value)}>
              <option value={OWN_MULTIPLIER}>{t('Own multiplier')}</option>
              {TALENTS.map((talent, index) => (
                <optgroup key={talent} label={t(talent)}>
                  {character.attacks.map((attack, at) =>
                    attack.talent === index ? (
                      <option key={`${attack.talent}:${attack.name}:${attack.name_ru}`} value={at}>
                        {language === 'ru' ? attack.name_ru : attack.name}
                      </option>
                    ) : null,
                  )}
                </optgroup>
              ))}
            </select>
          </label>
        ) : null}
        {parts.map((part, index) => {
          const labels = PART_LABELS[index] ?? PART_LABELS[1]
          return (
            <div key={labels.multiplier} className="pair">
              <label>
                {t(labels.multiplier)}
                <input
                  type="number"
                  inputMode="decimal"
                  min={0.1}
                  max={MAX_MULTIPLIER * PERCENT}
                  step="any"
                  value={part.percent}
                  onChange={(event) => change(index, { percent: event.target.value })}
                  required
                />
              </label>
              <label>
                {t(labels.scaling)}
                <select
                  value={part.stat}
                  onChange={(event) =>
                    change(index, { stat: choice(SCALINGS, event.target.value) })
                  }
                >
                  {Object.entries(SCALINGS).map(([scaling, label]) => (
                    <option key={scaling} value={scaling}>
                      {t(label)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )
        })}
        {character.attacks.length ? (
          <p className="hint">
            {t(
              "Multipliers from the game's tables at the character's talent levels, repeated hits added up. Check the damage bonus: it is a guess.",
            )}
          </p>
        ) : null}
        <label>
          {t('Damage bonus')}
          <select name="bonus" value={bonus} onChange={(event) => setBonus(event.target.value)}>
            <option value={NO_BONUS}>{t('None')}</option>
            {bonuses.map((stat) => (
              <option key={stat.key} value={stat.key}>
                {formatStat(stat, t)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t('Reaction')}
          <select name="reaction">
            {Object.entries(REACTIONS).map(([reaction, label]) => (
              <option key={reaction} value={reaction}>
                {t(label)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t('Enemy level')}
          <input
            name="enemy_level"
            type="number"
            inputMode="numeric"
            min={1}
            max={MAX_ENEMY_LEVEL}
            defaultValue={DEFAULT_ENEMY_LEVEL}
            required
          />
        </label>
        <label>
          {t('Enemy resistance, %')}
          <input
            name="enemy_resistance"
            type="number"
            inputMode="decimal"
            min={MIN_RESISTANCE * PERCENT}
            max={MAX_RESISTANCE * PERCENT}
            step="any"
            defaultValue={DEFAULT_RESISTANCE_PERCENT}
            required
          />
        </label>
        <details className="extras">
          <summary>{t('Team buffs and debuffs')}</summary>
          <label>
            {t('Flat damage added')}
            <input
              name="flat"
              type="number"
              inputMode="decimal"
              min={0}
              max={MAX_FLAT_DAMAGE}
              step="any"
              defaultValue={0}
              required
            />
          </label>
          <p className="hint">
            {t("Added to the hit's base: Shenhe's quills, Yun Jin's burst, Zhongli's passive.")}
          </p>
          <Reduction name="def_reduction" label="Enemy DEF reduction, %" max={PERCENT} />
          <Reduction name="def_ignore" label="Enemy DEF ignored, %" max={PERCENT} />
          <Reduction
            name="res_reduction"
            label="Enemy RES reduction, %"
            max={MAX_RESISTANCE * PERCENT}
          />
          <p className="hint">{t('DEF reduction counts up to 90%, as in the game.')}</p>
        </details>
        <button type="submit" disabled={state.status === 'loading'}>
          {t('Calculate damage')}
        </button>
      </form>
      {'message' in state && <p role="alert">{localized(state.message)}</p>}
      <div aria-live="polite">
        {'data' in state && (
          <dl>
            {RESULTS.map(({ label, key }) => (
              <div key={key}>
                <dt>{t(label)}</dt>
                <dd>{whole.format(state.data[key])}</dd>
              </div>
            ))}
          </dl>
        )}
      </div>
      {tried.length ? (
        <>
          <button
            type="button"
            className="secondary"
            disabled={trial.status === 'loading'}
            onClick={tryArtifacts}
          >
            {t('Try artifacts from the showcase')}
          </button>
          <p className="hint">
            {t(
              "For the hit above: each slot's best artifact among those the showcase's other characters wear. Set bonuses are not recounted.",
            )}
          </p>
          {'message' in trial && <p role="alert">{localized(trial.message)}</p>}
          <div aria-live="polite">
            {'data' in trial && <Trials comparison={trial.data} tried={tried} />}
          </div>
        </>
      ) : null}
    </details>
  )
}
