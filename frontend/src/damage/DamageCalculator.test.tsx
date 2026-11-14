import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import type { Character } from '../showcase/showcase'
import { DamageCalculator } from './DamageCalculator'

const AMBER: Character = {
  id: 10000021,
  name: 'Amber',
  element: 'pyro',
  level: 90,
  constellation: 6,
  talents: [10, 13, 13],
  stats: [
    { key: 'atk', value: 2000 },
    { key: 'crit_rate', value: 0.5 },
    { key: 'crit_dmg', value: 1 },
    { key: 'pyro_dmg', value: 0.466 },
    { key: 'physical_dmg', value: 0.25 },
  ],
  weapon: { name: 'Skyward Harp', rarity: 5, level: 90, refinement: 2, icon: null },
  artifacts: [],
  icon: null,
  attacks: [
    {
      talent: 0,
      name: '1-Hit DMG',
      name_ru: 'Урон атаки 1',
      scalings: [{ stat: 'atk', multiplier: 0.722 }],
    },
    {
      talent: 1,
      name: 'Tri-Karma DMG',
      name_ru: 'Урон Трёх карм',
      scalings: [
        { stat: 'atk', multiplier: 1.032 },
        { stat: 'elemental_mastery', multiplier: 2.064 },
      ],
    },
    {
      talent: 2,
      name: 'Fiery Rain DMG',
      name_ru: 'Урон огненного дождя',
      scalings: [{ stat: 'atk', multiplier: 0.505 }],
    },
  ],
}
const DAMAGE = { non_crit: 9000.4, crit: 18000.8, average: 13500.6 }

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function open(character: Character, respond: () => Promise<Response>): ReturnType<typeof vi.fn> {
  const fetchMock = vi.fn(respond)
  vi.stubGlobal('fetch', fetchMock)
  render(<DamageCalculator character={character} />)
  return fetchMock
}

const change = (label: string, value: string): boolean =>
  fireEvent.change(screen.getByLabelText(label), { target: { value } })

const calculate = (): boolean =>
  fireEvent.click(screen.getByRole('button', { name: 'Calculate damage' }))

const value = (label: string): string | null | undefined =>
  screen.getByText(label, { selector: 'dt' }).nextElementSibling?.textContent

/** The JSON body of the only request made. */
function sentBody(fetchMock: ReturnType<typeof vi.fn>): unknown {
  expect(fetchMock).toHaveBeenCalledOnce()
  const [url, init] = fetchMock.mock.calls[0]
  expect(url).toBe('/api/damage')
  expect(init.method).toBe('POST')
  return JSON.parse(init.body)
}

test('sends the character and the hit, with percents as fractions', async () => {
  const fetchMock = open(AMBER, async () => Response.json(DAMAGE))
  change('Talent multiplier, %', '392')
  change('Scales with', 'atk')
  change('Reaction', 'strong')
  change('Enemy level', '100')
  change('Enemy resistance, %', '10')
  calculate()
  await screen.findByText('13,501')
  expect(sentBody(fetchMock)).toEqual({
    level: 90,
    stats: AMBER.stats,
    scalings: [{ stat: 'atk', multiplier: 3.92 }],
    bonus: 'pyro_dmg',
    reaction: 'strong',
    flat: 0,
    enemy_level: 100,
    enemy_resistance: 0.1,
    def_reduction: 0,
    def_ignore: 0,
    res_reduction: 0,
  })
})

test('a hit from the talent tables fills in its multiplier and a likely bonus', async () => {
  const fetchMock = open(AMBER, async () => Response.json(DAMAGE))
  const hits = screen.getByLabelText<HTMLSelectElement>('Hit')
  expect([...hits.querySelectorAll('optgroup')].map((group) => group.label)).toEqual([
    'Normal Attack',
    'Elemental Skill',
    'Elemental Burst',
  ])
  change('Hit', '2')
  expect(screen.getByLabelText<HTMLInputElement>('Talent multiplier, %').value).toBe('50.5')
  expect(screen.getByLabelText<HTMLSelectElement>('Damage bonus').value).toBe('pyro_dmg')
  change('Hit', '0') // a Normal Attack is taken as Physical
  expect(screen.getByLabelText<HTMLSelectElement>('Damage bonus').value).toBe('physical_dmg')
  change('Talent multiplier, %', '80') // the number can still be changed by hand
  calculate()
  await screen.findByText('13,501')
  expect(sentBody(fetchMock)).toMatchObject({ scalings: [{ stat: 'atk', multiplier: 0.8 }] })
})

test('a hit that scales with two stats sends both', async () => {
  const fetchMock = open(AMBER, async () => Response.json(DAMAGE))
  change('Hit', '1')
  expect(screen.getByLabelText<HTMLInputElement>('Second part, %').value).toBe('206.4')
  expect(screen.getByLabelText<HTMLSelectElement>('Second part scales with').value).toBe(
    'elemental_mastery',
  )
  calculate()
  await screen.findByText('13,501')
  expect(sentBody(fetchMock)).toMatchObject({
    scalings: [
      { stat: 'atk', multiplier: 1.032 },
      { stat: 'elemental_mastery', multiplier: 2.064 },
    ],
  })
  change('Hit', '') // back to a multiplier of one's own: one part
  expect(screen.queryByLabelText('Second part, %')).toBeNull()
})

test("the team's help goes in as fractions", async () => {
  const fetchMock = open(AMBER, async () => Response.json(DAMAGE))
  change('Flat damage added', '1500')
  change('Enemy DEF reduction, %', '30')
  change('Enemy DEF ignored, %', '60')
  change('Enemy RES reduction, %', '40')
  change('Reaction', 'aggravate')
  calculate()
  await screen.findByText('13,501')
  expect(sentBody(fetchMock)).toMatchObject({
    flat: 1500,
    def_reduction: 0.3,
    def_ignore: 0.6,
    res_reduction: 0.4,
    reaction: 'aggravate',
  })
})

test('hit names follow the language', async () => {
  const { setLanguage } = await import('../i18n')
  setLanguage('ru')
  try {
    open(AMBER, async () => Response.json(DAMAGE))
    const names = [...screen.getByLabelText<HTMLSelectElement>('Удар').options].map(
      (option) => option.textContent,
    )
    expect(names).toContain('Урон огненного дождя')
  } finally {
    setLanguage('en')
  }
})

test('shows average, crit and non-crit damage', async () => {
  open(AMBER, async () => Response.json(DAMAGE))
  calculate()
  await screen.findByText('13,501')
  expect([value('Average'), value('Crit'), value('Non-crit')]).toEqual(['13,501', '18,001', '9,000'])
})

test('offers the bonuses the character has, the first one chosen', () => {
  open(AMBER, async () => Response.json(DAMAGE))
  const options = [...screen.getByLabelText<HTMLSelectElement>('Damage bonus').options]
  expect(options.map((option) => option.textContent)).toEqual([
    'None',
    'Pyro DMG 46.6%',
    'Physical DMG 25%',
  ])
  expect(screen.getByLabelText<HTMLSelectElement>('Damage bonus').value).toBe('pyro_dmg')
})

test('sends no bonus when none is chosen', async () => {
  const fetchMock = open(AMBER, async () => Response.json(DAMAGE))
  change('Damage bonus', '')
  calculate()
  await screen.findByText('13,501')
  expect(sentBody(fetchMock)).toMatchObject({ bonus: null })
})

test('a character without bonuses starts with none', () => {
  const plain = { ...AMBER, stats: [{ key: 'atk', value: 2000 } as const] }
  open(plain, async () => Response.json(DAMAGE))
  expect(screen.getByLabelText<HTMLSelectElement>('Damage bonus').value).toBe('')
})

test.each([
  { name: 'refused request', respond: async () => Response.json({ detail: 'Too many requests.' }, { status: 429 }) },
  { name: 'unexpected body', respond: async () => Response.json({ average: 'a lot' }) },
])('$name shows an error and allows a retry', async ({ respond }) => {
  open(AMBER, respond)
  calculate()
  expect(await screen.findByRole('alert')).toBeDefined()
  expect(screen.getByRole('button', { name: 'Calculate damage' })).toHaveProperty('disabled', false)
})
