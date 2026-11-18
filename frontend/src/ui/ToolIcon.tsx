import { useId, type JSX } from 'react'

// The tools' signs are drawn for this app on a 24px grid, in the text colour, after the games'
// own menu signs so players know them: none is traced from the game's art. Each is a list of
// filled shapes; a shape with holes in it is drawn even-odd.
const SIGNS = {
  // The start page: three tiles and a star.
  home: [
    'M5.5 3h3A2.5 2.5 0 0 1 11 5.5v3A2.5 2.5 0 0 1 8.5 11h-3A2.5 2.5 0 0 1 3 8.5v-3A2.5 2.5 0 0 1 5.5 3Z',
    'M15.5 3h3A2.5 2.5 0 0 1 21 5.5v3a2.5 2.5 0 0 1-2.5 2.5h-3A2.5 2.5 0 0 1 13 8.5v-3A2.5 2.5 0 0 1 15.5 3Z',
    'M5.5 13h3a2.5 2.5 0 0 1 2.5 2.5v3A2.5 2.5 0 0 1 8.5 21h-3A2.5 2.5 0 0 1 3 18.5v-3A2.5 2.5 0 0 1 5.5 13Z',
    'M17 12.5c.6 3.1 1.4 3.9 4.5 4.5-3.1.6-3.9 1.4-4.5 4.5-.6-3.1-1.4-3.9-4.5-4.5 3.1-.6 3.9-1.4 4.5-4.5Z',
  ],
  // Star Rail builds: a bob of hair with pointed locks; CUTS draws the face's edge and a strand.
  builds: [
    'M12 1.5C6.4 1.5 2.8 5 2.8 10.2L2.7 12.8C2.5 15 2 17.6 1.2 19.6C2.5 19.3 3.6 18.6 4.4 17.8L4.2 21.4L5.6 18.8C7 20.6 8.8 22.2 9.9 23.6L8.7 18.4C9.8 18.1 11 18 12.2 18C13.4 18 14.4 18.1 15.4 18.4L14.4 23.6C15.6 22.2 17.2 20.6 18.6 18.8L19.8 21.4L19.6 17.8C20.4 18.6 21.5 19.3 22.8 19.6C22 17.6 21.5 15 21.3 12.8L21.2 10.2C21.2 5 17.6 1.5 12 1.5Z',
  ],
  // Genshin builds: two characters in profile, facing right; the front one has a tuft and an earring.
  'gi-builds': [
    'M5.36 5.87C7.2 5.87 8.49 6.52 9.32 7.53L10.33 7.34L9.96 8.45C10.14 8.91 10.24 9.28 10.24 9.74L11.25 10.1L10.33 10.75L10.97 11.94L10.05 12.22C10.24 12.96 10.42 13.6 10.97 14.24L10.33 14.61C10.42 15.07 10.24 15.44 9.78 15.62C9.59 15.99 9.13 16.27 8.58 16.27L8.86 18.38L4.16 19.12L5.08 16.91C4.35 16.73 3.43 16.91 2.42 17.65C2.78 16.82 2.88 16.27 2.6 15.81C1.77 16.18 1.04 16.08 0.3 15.72C1.13 15.26 1.22 14.7 1.04 14.06L0.21 13.14L1.04 12.68C0.76 11.85 0.76 11.02 0.94 10.29L0.3 9.37L1.5 9.18C1.96 8.08 2.69 7.16 3.61 6.52L3.8 5.6L4.62 6.06C4.9 5.96 5.08 5.87 5.36 5.87Z',
    'M3.24 6.79C2.51 6.15 2.6 5.23 3.43 4.86C3.24 5.6 3.61 6.15 4.26 6.42Z',
    'M17.76 5.67C19.6 5.67 20.89 6.32 21.72 7.33L22.73 7.14L22.36 8.25C22.54 8.71 22.64 9.08 22.64 9.54L23.65 9.9L22.73 10.55L23.37 11.74L22.45 12.02C22.64 12.76 22.82 13.4 23.37 14.04L22.73 14.41C22.82 14.87 22.64 15.24 22.18 15.42C21.99 15.79 21.53 16.07 20.98 16.07L21.26 18.18L16.56 18.92L17.48 16.71C16.75 16.53 15.83 16.71 14.82 17.45C15.18 16.62 15.28 16.07 15 15.61C14.17 15.98 13.44 15.88 12.7 15.52C13.53 15.06 13.62 14.5 13.44 13.86L12.61 12.94L13.44 12.48C13.16 11.65 13.16 10.82 13.34 10.09L12.7 9.17L13.9 8.98C14.36 7.88 15.09 6.96 16.01 6.32L16.2 5.4L17.02 5.86C17.3 5.76 17.48 5.67 17.76 5.67Z',
  ],
  // Relics: a Planar Ornament's ring between two arcs.
  relics: [
    'M17.4 12a5.4 5.4 0 1 1-10.8 0 5.4 5.4 0 0 1 10.8 0ZM15.4 12a3.4 3.4 0 1 0-6.8 0 3.4 3.4 0 0 0 6.8 0ZM13.3 12a1.3 1.3 0 1 1-2.6 0 1.3 1.3 0 0 1 2.6 0Z',
    'M7.31 3.17A10 10 0 0 0 7.31 20.83L8.34 18.89A7.8 7.8 0 0 1 8.34 5.11Z',
    'M16.69 3.17A10 10 0 0 1 16.69 20.83L15.66 18.89A7.8 7.8 0 0 0 15.66 5.11Z',
  ],
  // Warps: four petals to the corners, each an outline round a smaller one.
  warps: [
    'M12 12C7.5 12 3.5 8 3 3c5 .5 9 4.5 9 9ZM11 11C8 10.8 5.3 8.2 5 5c3.2.3 5.8 3 6 6ZM10 10C8.4 9.7 7.2 8.6 7 7c1.6.2 2.7 1.4 3 3Z',
    'M12 12c0-4.5 4-8.5 9-9-.5 5-4.5 9-9 9ZM13 11c.2-3 2.8-5.7 6-6-.3 3.2-3 5.8-6 6ZM14 10c.3-1.6 1.4-2.8 3-3-.2 1.6-1.4 2.7-3 3Z',
    'M12 12c4.5 0 8.5 4 9 9-5-.5-9-4.5-9-9ZM13 13c3 .2 5.7 2.8 6 6-3.2-.3-5.8-3-6-6ZM14 14c1.6.3 2.8 1.4 3 3-1.6-.2-2.7-1.4-3-3Z',
    'M12 12c0 4.5-4 8.5-9 9 .5-5 4.5-9 9-9ZM11 13c-.2 3-2.8 5.7-6 6 .3-3.2 3-5.8 6-6ZM10 14c-.3 1.6-1.4 2.8-3 3 .2-1.6 1.4-2.7 3-3Z',
  ],
  // Genshin wishes: a great four-pointed star and a small one.
  'gi-wishes': [
    'M10.5 5c.7 5.5 2 6.8 8 8-6 1.2-7.3 2.5-8 8-.7-5.5-2-6.8-8-8 6-1.2 7.3-2.5 8-8Z',
    'M18 2.5c.3 2.1.9 2.7 3 3-2.1.3-2.7.9-3 3-.3-2.1-.9-2.7-3-3 2.1-.3 2.7-.9 3-3Z',
  ],
  // Star Rail history: a page of records under a magnifying glass.
  history: [
    'M6 2.5h8.5a2 2 0 0 1 2 2v5.92A5.6 5.6 0 0 0 14.95 21.5H6a2 2 0 0 1-2-2v-15a2 2 0 0 1 2-2ZM7 6h7v1.6H7ZM7 9.6h4.5v1.6H7ZM7 13.2h2.5v1.6H7Z',
    'M19.8 16a3.8 3.8 0 1 1-7.6 0 3.8 3.8 0 0 1 7.6 0ZM18.2 16a2.2 2.2 0 1 0-4.4 0 2.2 2.2 0 0 0 4.4 0Z',
    'M18.3 19.7 19.7 18.3l1.9 1.9a1 1 0 0 1-1.4 1.4Z',
  ],
  // Genshin history: an open book with a ribbon.
  'gi-history': [
    'M2.5 5.5c2.5-.9 6-.7 8.7.8V20c-2.7-1.4-6.2-1.6-8.7-.7ZM5 9h4v1.2H5ZM5 12h4.5v1.2H5ZM5 15h3v1.2H5Z',
    'M12.8 6.3c2.7-1.5 6.2-1.7 8.7-.8v13.8c-2.5-.9-6-.7-8.7.7ZM17 6.6V11l1.2-1 1.2 1V6.4Z',
  ],
  // Speed: a high boot with a wing at the heel.
  speed: [
    'M10 3H15.5C16.3 3 16.9 3.7 16.8 4.5L16 12.5C16.6 13.6 17 15 17 16.5V17.8C17 18.5 16.5 19 15.8 19H4.3C3.4 19 2.8 18.2 3.1 17.4 3.6 15.8 5 14.8 6.7 14.5L9.4 13.9ZM4.2 16.9H16.1V17.8H4.2Z',
    'M17.3 3.8C19.6 3.4 21.6 4.2 22.6 6 21.2 5.7 19.9 5.8 18.7 6.4Z',
    'M17 7.2C19 7 20.7 7.8 21.6 9.4 20.4 9.1 19.3 9.2 18.3 9.7Z',
  ],
} as const

// Thin lines cut out of a sign, where the game's sign shows an edge inside the shape.
const CUTS: Partial<Record<keyof typeof SIGNS, string>> = {
  // The face's edge, the strand above it, and the locks' partings.
  builds:
    'M10 4.4C9.7 6.4 9.6 8.4 9.8 10.1M9.8 10.1L13.3 14.6L14 9.2C15.5 10.2 16.3 11.6 16.2 13.3C16 15.6 14.5 17.3 12.3 17.5C10.1 17.3 8.5 15.7 8.4 13.5C8.4 12.1 8.9 10.9 9.8 10.1ZM5 12.2C5.1 15.4 6.6 18 9.3 20.6M19 12.2C18.9 15.4 17.4 18 14.8 20.6',
  // Where the front one's hair meets the face, and the earring; the same line on the back one.
  'gi-builds':
    'M9.22 12.31C8.67 13.23 8.49 14.15 8.67 15.26M7.43 15.81A0.370.37 0 1 1 6.69 15.81A0.370.37 0 1 1 7.43 15.81M21.62 12.11C21.07 13.03 20.89 13.95 21.07 15.06',
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
