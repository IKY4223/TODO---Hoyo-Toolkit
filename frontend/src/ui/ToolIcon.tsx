import type { JSX } from 'react'

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
  // Star Rail builds: a character's head, shaggy hair round the face.
  builds: [
    'M12 2C8.5 2 5.5 4 4.6 7.6c-.5 2.1-.2 4.4-1.4 6.6 1.2-.2 2.1-.8 2.6-1.6.1 2.7 1 5.2 2.5 7.2l1-1.9c.9.7 1.8 1.1 2.7 1.1s1.8-.4 2.7-1.1l1 1.9c1.5-2 2.4-4.5 2.5-7.2.5.8 1.4 1.4 2.6 1.6-1.2-2.2-.9-4.5-1.4-6.6C18.5 4 15.5 2 12 2ZM7.8 10.6l1.8-2.4 1.2 1.8 2.4-3.1.7 2.5 2.3-.8c.2.7.2 1.4.2 2-.2 3.5-2.1 6.1-4.4 6.1s-4.1-2.5-4.2-6.1Z',
    'M12.5 2.4c.5-1.2 1.7-1.8 3-1.6-.9.5-1.5 1.2-1.6 2Z',
  ],
  // Genshin builds: two characters face to face.
  'gi-builds': [
    'M2.1 7.2C2.9 4.6 5.3 3.2 7.7 3.6 9.8 4 10.9 5.9 10.6 8L11.4 9.8C11.5 10 11.4 10.2 11.1 10.3L10.4 10.5 10.3 11.9C10.2 12.7 9.5 13.2 8.7 13.1L7.8 13 8 15H3.7C3.6 13.6 2.9 12.7 2.2 11.9 1.2 10.6 1.6 8.8 2.1 7.2Z',
    'M5.6 3.9C5.9 2.4 7 1.6 8.4 1.7 7.8 2.2 7.5 2.9 7.6 3.6Z',
    'M1.8 20.5C2.1 17.6 4.1 15.7 6.9 15.7S11.2 17.6 11.4 20.5Z',
    'M21.9 7.2C21.1 4.6 18.7 3.2 16.3 3.6 14.2 4 13.1 5.9 13.4 8L12.6 9.8C12.5 10 12.6 10.2 12.9 10.3L13.6 10.5 13.7 11.9C13.8 12.7 14.5 13.2 15.3 13.1L16.2 13 16 15H20.3C20.4 13.6 21.1 12.7 21.8 11.9 22.8 10.6 22.4 8.8 21.9 7.2Z',
    'M18.4 3.9C18.1 2.4 17 1.6 15.6 1.7 16.2 2.2 16.5 2.9 16.4 3.6Z',
    'M22.2 20.5C21.9 17.6 19.9 15.7 17.1 15.7S12.8 17.6 12.6 20.5Z',
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
      ) : (
        SIGNS[name].map((d) => (
          <path key={d} d={d} fill="currentColor" fillRule="evenodd" />
        ))
      )}
    </svg>
  )
}
