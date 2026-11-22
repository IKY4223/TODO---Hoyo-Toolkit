import { expect, test } from 'vitest'
import { translate } from './i18n'

test.each([
  [1, 'lasts 1 turn', 'длится 1 ход'],
  [2, 'lasts 2 turns', 'длится 2 хода'],
  [5, 'lasts 5 turns', 'длится 5 ходов'],
  [21, 'lasts 21 turns', 'длится 21 ход'],
])('a count of %i takes the word its language gives that number', (turns, en, ru) => {
  expect(translate('en', 'lasts {turns} {turns|turn|turns}', { turns })).toBe(en)
  expect(translate('ru', 'lasts {turns} {turns|turn|turns}', { turns })).toBe(ru)
})
