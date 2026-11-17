import { useId, type JSX } from 'react'

// The tools' signs are drawn for this app on a 24px grid, in the text colour, after the games'
// own menu signs so players know them: none is traced from the game's art. Each is a list of
// filled shapes; a shape with holes in it is drawn even-odd.
const SIGNS = {
  // The start page: three tiles and a diamond ring.
  home: [
    'M5 3.6H9.2A1.6 1.6 0 0 1 10.8 5.2V9.4A1.6 1.6 0 0 1 9.2 11H5A1.6 1.6 0 0 1 3.4 9.4V5.2A1.6 1.6 0 0 1 5 3.6Z',
    'M14.2 3.6H18.4A1.6 1.6 0 0 1 20 5.2V9.4A1.6 1.6 0 0 1 18.4 11H14.2A1.6 1.6 0 0 1 12.6 9.4V5.2A1.6 1.6 0 0 1 14.2 3.6Z',
    'M5 12.8H9.2A1.6 1.6 0 0 1 10.8 14.4V18.6A1.6 1.6 0 0 1 9.2 20.2H5A1.6 1.6 0 0 1 3.4 18.6V14.4A1.6 1.6 0 0 1 5 12.8Z',
    'M14.8 13.4Q16.3 11.9 17.8 13.4L19.4 15Q20.9 16.5 19.4 18L17.8 19.6Q16.3 21.1 14.8 19.6L13.2 18Q11.7 16.5 13.2 15ZM15.8 14.25Q16.3 13.75 16.8 14.25L18.55 16Q19.05 16.5 18.55 17L16.8 18.75Q16.3 19.25 15.8 18.75L14.05 17Q13.55 16.5 14.05 16Z',
  ],
  // Star Rail builds: a bob of hair with pointed locks; CUTS draws the face's edge and a strand.
  builds: [
    'M12 1.5C6.4 1.5 2.8 5 2.8 10.2L2.7 12.8C2.5 14.6 2.1 16 1.4 17.4C2.6 17.3 3.6 16.9 4.4 16.2L4.3 19.2L5.6 17C7 19 9 21 10.3 22.8L10.7 19.2H13.3L14.4 22.6C16 21 17.6 19.2 18.6 17L19.8 19.2L19.6 16.2C20.4 16.9 21.4 17.3 22.6 17.4C21.9 16 21.5 14.6 21.3 12.8L21.2 10.2C21.2 5 17.6 1.5 12 1.5Z',
  ],
  // Genshin builds: two characters in profile, facing right; the front one has a tuft and an earring.
  'gi-builds': [
    'M5.8 5.5C7.6 5.2 9 5.9 9.5 6.9L10.6 7.1L9.8 7.9C10 8.7 9.9 9.6 9.7 10.4L10.7 12.2L9.8 12.5C9.9 13.2 9.6 13.8 8.9 13.9L9.4 17.5L3.4 18.8L4.4 16.6L2 15.2L3.6 14.6L1 13L2.2 12.4L0.6 10.2C0.4 8.6 0.9 7.3 1.9 6.4L1.4 5.6L3 5.8C3.8 5.6 4.8 5.5 5.8 5.5Z',
    'M4.3 5.9C3.7 5.1 3.9 4.2 4.8 4C4.5 4.7 4.7 5.3 5.2 5.7Z',
    'M16.6 5.5C18.6 5.4 20.3 6.4 21.1 7.8L22.2 8.1L21.5 8.9L22.4 9.6L21.8 10.2L23.6 11.3L21.9 12C22 12.8 21.6 13.4 20.9 13.5L21.6 15.6L20.2 15.4L19.6 17.5L15 18.6L16.4 16.8L14.2 15.8L15.4 15L12.8 13.6L13.6 12.6L12.4 10.4C12.2 8.8 12.7 7.5 13.6 6.5L13.1 5.7L14.8 5.9C15.4 5.6 16 5.5 16.6 5.5Z',
  ],
  // Relics: a ring inside a sphere of curved bands, after the Planar Ornament's sign.
  relics: [
    'M16.8 12A4.8 4.8 0 1 1 7.2 12A4.8 4.8 0 1 1 16.8 12ZM15.7 12A3.7 3.7 0 1 0 8.3 12A3.7 3.7 0 1 0 15.7 12Z',
    'M8.1 6.7C8.2 5.2 8.6 4 9.3 3.2C10.1 2.7 11 2.5 12 2.5C13 2.5 13.9 2.7 14.7 3.2C15.4 4 15.8 5.2 15.9 6.7C14.8 6 13.4 5.6 12 5.6C10.6 5.6 9.2 6 8.1 6.7Z',
    'M8.1 17.3C8.2 18.8 8.6 20 9.3 20.8C10.1 21.3 11 21.5 12 21.5C13 21.5 13.9 21.3 14.7 20.8C15.4 20 15.8 18.8 15.9 17.3C14.8 18 13.4 18.4 12 18.4C10.6 18.4 9.2 18 8.1 17.3Z',
    'M8.4 3.6C7.6 4.6 7 5.6 6.8 6.8C6.4 7.8 6.1 8.8 6 9.8L4 10.3C4.2 7.4 5.9 5 8.4 3.6Z',
    'M15.6 3.6C16.4 4.6 17 5.6 17.2 6.8C17.6 7.8 17.9 8.8 18 9.8L20 10.3C19.8 7.4 18.1 5 15.6 3.6Z',
    'M8.4 20.4C7.6 19.4 7 18.4 6.8 17.2C6.4 16.2 6.1 15.2 6 14.2L4 13.7C4.2 16.6 5.9 19 8.4 20.4Z',
    'M15.6 20.4C16.4 19.4 17 18.4 17.2 17.2C17.6 16.2 17.9 15.2 18 14.2L20 13.7C19.8 16.6 18.1 19 15.6 20.4Z',
    'M4.4 6.6C3.2 8 2.7 10 2.7 12C2.7 14 3.2 16 4.4 17.4C2 16.6 0.7 14.4 0.7 12C0.7 9.6 2 7.4 4.4 6.6Z',
    'M19.6 6.6C20.8 8 21.3 10 21.3 12C21.3 14 20.8 16 19.6 17.4C22 16.6 23.3 14.4 23.3 12C23.3 9.6 22 7.4 19.6 6.6Z',
  ],
  // Warps: a four-petal frame round a flower; CUTS draws the inner outline.
  warps: [
    'M2.8 2.8L8.2 2.8C10.2 2.8 11.5 4.4 12 6.6C12.5 4.4 13.8 2.8 15.8 2.8L21.2 2.8L21.2 8.2C21.2 10.2 19.6 11.5 17.4 12C19.6 12.5 21.2 13.8 21.2 15.8L21.2 21.2L15.8 21.2C13.8 21.2 12.5 19.6 12 17.4C11.5 19.6 10.2 21.2 8.2 21.2L2.8 21.2L2.8 15.8C2.8 13.8 4.4 12.5 6.6 12C4.4 11.5 2.8 10.2 2.8 8.2ZM12 12C13.6 11.9 14.7 10.8 14.9 9.1C13.2 9.3 12.1 10.4 12 12ZM12 12C10.4 11.9 9.3 10.8 9.1 9.1C10.8 9.3 11.9 10.4 12 12ZM12 12C10.4 12.1 9.3 13.2 9.1 14.9C10.8 14.7 11.9 13.6 12 12ZM12 12C13.6 12.1 14.7 13.2 14.9 14.9C13.2 14.7 12.1 13.6 12 12Z',
  ],
  // Genshin wishes: a great four-pointed star and two small ones.
  'gi-wishes': [
    'M11 1.8C12.15 8.3 14.36 10.6 20.6 11.8C14.36 13 12.15 15.3 11 21.8C9.85 15.3 7.64 13 1.4 11.8C7.64 10.6 9.85 8.3 11 1.8Z',
    'M4.4 1.9C4.68 3.53 5.21 4.1 6.7 4.4C5.21 4.7 4.68 5.28 4.4 6.9C4.12 5.28 3.6 4.7 2.1 4.4C3.6 4.1 4.12 3.53 4.4 1.9Z',
    'M18.6 15.4C18.96 17.48 19.65 18.22 21.6 18.6C19.65 18.98 18.96 19.72 18.6 21.8C18.24 19.72 17.55 18.98 15.6 18.6C17.55 18.22 18.24 17.48 18.6 15.4Z',
  ],
  // Star Rail history: a page of records under a magnifying glass; CUTS draws the page's inner edge.
  history: [
    'M5.7 2.5H18.3A.8.8 0 0 1 19.1 3.3V20.27L17.43 18.59A3.8 3.8 0 1 0 15.94 20.08L17.12 21.25H5.7A.8.8 0 0 1 4.9 20.45V3.3A.8.8 0 0 1 5.7 2.5ZM9.18 6.2A0.68 0.68 0 1 0 7.82 6.2A0.68 0.68 0 1 0 9.18 6.2ZM10.88 5.82H15.52A0.38 0.38 0 0 1 15.9 6.2V6.2A0.38 0.38 0 0 1 15.52 6.58H10.88A0.38 0.38 0 0 1 10.5 6.2V6.2A0.38 0.38 0 0 1 10.88 5.82ZM8.18 7.82H13.22A0.38 0.38 0 0 1 13.6 8.2V8.2A0.38 0.38 0 0 1 13.22 8.58H8.18A0.38 0.38 0 0 1 7.8 8.2V8.2A0.38 0.38 0 0 1 8.18 7.82ZM16.38 8.2A0.68 0.68 0 1 0 15.02 8.2A0.68 0.68 0 1 0 16.38 8.2ZM9.18 10.2A0.68 0.68 0 1 0 7.82 10.2A0.68 0.68 0 1 0 9.18 10.2ZM10.88 9.82H15.52A0.38 0.38 0 0 1 15.9 10.2V10.2A0.38 0.38 0 0 1 15.52 10.58H10.88A0.38 0.38 0 0 1 10.5 10.2V10.2A0.38 0.38 0 0 1 10.88 9.82Z',
    'M17.15 16.75A3.05 3.05 0 1 1 11.05 16.75A3.05 3.05 0 1 1 17.15 16.75ZM16.4 16.75A2.3 2.3 0 1 0 11.8 16.75A2.3 2.3 0 1 0 16.4 16.75Z',
    'M16.54 18.41L18.94 20.81A.55.55 0 0 1 18.16 21.59L15.76 19.19Z',
  ],
  // Genshin history: an open book with lines and a bookmark.
  'gi-history': [
    'M11.4 5.2C8.9 3.8 5.2 3.4 1.6 3.9V19.4C5.2 18.9 8.9 19.3 11.4 20.6ZM4.18 6.22H9.02A0.38 0.38 0 0 1 9.4 6.6V6.6A0.38 0.38 0 0 1 9.02 6.98H4.18A0.38 0.38 0 0 1 3.8 6.6V6.6A0.38 0.38 0 0 1 4.18 6.22ZM4.18 8.42H6.62A0.38 0.38 0 0 1 7 8.8V8.8A0.38 0.38 0 0 1 6.62 9.18H4.18A0.38 0.38 0 0 1 3.8 8.8V8.8A0.38 0.38 0 0 1 4.18 8.42Z',
    'M12.6 5.2C15.1 3.8 18.8 3.4 22.4 3.9V19.4C18.8 18.9 15.1 19.3 12.6 20.6ZM17.8 4.3H20.2V8.9L19 7.8L17.8 8.9Z',
  ],
  // Speed: a running figure under a curved band, after the game's Speed sign.
  speed: [
    'M9.9 4.3C13.4 4.3 16.4 6.6 18 10.2L16.4 11C15.4 7.9 13 5.7 9.7 5.6Z',
    'M9.8 6.3C12.6 6.5 14.9 8.4 15.8 11.2L13.2 13C13 13.6 13.3 14.1 13.9 14.3C16 14.9 17.5 16.9 17.9 19.4L12.3 19.8C11.1 18.3 9.6 17.2 8.3 16.9C7.9 17.3 7.6 17.8 7.4 18L4.2 15.8L4.8 14C5.7 12.4 6.8 11.1 8 10.5C8.6 9.2 9.2 7.6 9.8 6.3Z',
  ],
} as const

// Thin lines cut out of a sign, where the game's sign shows an edge inside the shape.
const CUTS: Partial<Record<keyof typeof SIGNS, string>> = {
  // The face's edge, the strand above it, and the locks' partings.
  builds:
    'M10 4.4C9.7 6.4 9.6 8.4 9.8 10.1M9.8 10.1L13.3 14.6L14 9.2C15.5 10.2 16.3 11.6 16.2 13.3C16 15.6 14.5 17.3 12.3 17.5C10.1 17.3 8.5 15.7 8.4 13.5C8.4 12.1 8.9 10.9 9.8 10.1ZM5 12.2C5.1 15 6.6 17 8.6 18.4M19 12.2C18.9 15 17.4 17 15.4 18.4',
  // Where the front one's hair meets the face, and the earring; the same line on the back one.
  'gi-builds':
    'M8.3 9.1C7.5 10.5 7.5 12.1 8.1 13.3M6.75 14.4A.35.35 0 1 1 6.05 14.4A.35.35 0 1 1 6.75 14.4M19.4 9.4C18.8 10.8 18.9 12.4 19.6 13.4',
  // The inner outline, parting the frame from the flower.
  warps:
    'M4.27 4.27L8.81 4.27C10.49 4.27 11.58 5.62 12 7.46C12.42 5.62 13.51 4.27 15.19 4.27L19.73 4.27L19.73 8.81C19.73 10.49 18.38 11.58 16.54 12C18.38 12.42 19.73 13.51 19.73 15.19L19.73 19.73L15.19 19.73C13.51 19.73 12.42 18.38 12 16.54C11.58 18.38 10.49 19.73 8.81 19.73L4.27 19.73L4.27 15.19C4.27 13.51 5.62 12.42 7.46 12C5.62 11.58 4.27 10.49 4.27 8.81Z',
  // The page's inner edge, stopping short of the glass's handle.
  history:
    'M18.05 19.2V4.3A.75.75 0 0 0 17.3 3.55H6.7A.75.75 0 0 0 5.95 4.3V19.45A.75.75 0 0 0 6.7 20.2H12.4',
}

// The theme button's signs stay line drawings.
const LINES = {
  // The light theme.
  sun:
    'M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6',
  // The dark theme.
  moon:
    'M20 14.6A8.2 8.2 0 1 1 9.4 4a6.6 6.6 0 0 0 10.6 10.6Z',
  // Half light, half dark: the theme on the device.
  auto:
    'M20.5 12a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0ZM12 3.5v17',
} as const

export type ToolIconName = keyof typeof SIGNS | keyof typeof LINES

function isLine(name: ToolIconName): name is keyof typeof LINES {
  return Object.hasOwn(LINES, name)
}

/** A tool's icon, beside its name: decorative, hidden from screen readers. */
export function ToolIcon({ name }: { readonly name: ToolIconName }): JSX.Element {
  const mask = `cut-${useId().replace(/[^\w-]/g, '')}` // a url(#…) reference wants a plain id
  const cut = isLine(name) ? undefined : CUTS[name]
  const fills = isLine(name)
    ? null
    : SIGNS[name].map((d) => <path key={d} d={d} fill="currentColor" fillRule="evenodd" />)
  return (
    <svg
      viewBox="0 0 24 24"
      width="24"
      height="24"
      aria-hidden="true"
      className="tool-icon"
      data-icon={name}
    >
      {isLine(name) ? (
        <path
          d={LINES[name]}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      ) : cut ? (
        <>
          <mask id={mask}>
            <rect width="24" height="24" fill="white" />
            <path
              d={cut}
              fill="none"
              stroke="black"
              strokeWidth="1.1"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </mask>
          <g mask={`url(#${mask})`}>{fills}</g>
        </>
      ) : (
        fills
      )}
    </svg>
  )
}
