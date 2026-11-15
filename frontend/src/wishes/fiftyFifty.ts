import { CHARACTER_BANNERS, CHARACTER_NAMES, type GenshinBanner } from './genshin-banners'
import type { Pull } from './history'

/** The 50/50s a history shows: won, lost, and 5★ pulls it cannot tell about. */
export interface FiftyFifty {
  readonly won: number
  readonly lost: number
  /** A first 5★ that won (a loss before the history may have guaranteed it), a 5★ outside
   * every known banner, or one named in a language the banner list does not use. */
  readonly uncounted: number
}

const ASIA_OFFSET = 8 // the banner list's times are the Asia server's, UTC+8
const HOUR_MS = 3_600_000
const DATE_LENGTH = 19 // "2026-01-10 12:00:00"

/** A server time moved by `hours`, in the same "YYYY-MM-DD HH:mm:ss" form. */
function shift(time: string, hours: number): string {
  const moved = new Date(Date.parse(`${time.replace(' ', 'T')}Z`) + hours * HOUR_MS)
  return moved.toISOString().slice(0, DATE_LENGTH).replace('T', ' ')
}

/** The characters featured when a pull was made, on the player's server; null if none known. */
function featuredAt(
  time: string,
  offset: number,
  banners: readonly GenshinBanner[],
): ReadonlySet<string> | null {
  // As paimon.moe's src/functions/wish.js: an Asia time moves to the player's server.
  const local = (when: string, asia: boolean): string =>
    asia ? shift(when, offset - ASIA_OFFSET) : when
  const running = banners.filter(
    (banner) =>
      local(banner.start, banner.startAsia) <= time && time <= local(banner.end, banner.endAsia),
  )
  return running.length ? new Set(running.flatMap((banner) => banner.featured)) : null
}

/**
 * The 50/50s among a character event pool's 5★ pulls, oldest first. A 5★ after a lost 50/50 is
 * guaranteed, so it is no 50/50; Capturing Radiance changes the odds of a 50/50, not what it is.
 * `offset` is the player's server's UTC offset in hours.
 */
export function fiftyFifty(
  fives: readonly Pull[],
  offset: number,
  banners: readonly GenshinBanner[] = CHARACTER_BANNERS,
  names: ReadonlySet<string> = CHARACTER_NAMES,
): FiftyFifty {
  let [won, lost, uncounted] = [0, 0, 0]
  // Whether the next 5★ is guaranteed: unknown at first and after a 5★ that could not be read.
  let guaranteed: boolean | null = null
  for (const five of fives) {
    const featured = featuredAt(five.time, offset, banners)
    if (!featured || !names.has(five.name)) {
      uncounted += 1
      guaranteed = null
      continue
    }
    const win = featured.has(five.name)
    if (guaranteed === false) {
      if (win) won += 1
      else lost += 1
    } else if (guaranteed === null) {
      // A loss is a 50/50 for certain; a win may have been a guarantee.
      if (win) uncounted += 1
      else lost += 1
    }
    guaranteed = !win
  }
  return { won, lost, uncounted }
}
