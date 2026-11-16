import type { JSX } from 'react'

// Every icon is drawn for this app on a 24px grid, in the text colour: none is the game's art.
const PATHS = {
  // The start page: a house.
  home: 'M3.5 11 12 3.5l8.5 7.5M5.5 9.5v11h13v-11M10 20.5v-6h4v6',
  // A character and their gear: a person.
  builds: 'M16 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM4.5 20.5a7.5 7.5 0 0 1 15 0',
  // Relics: a cut gem.
  relics: 'M7 4h10l4 5.5-9 10.5L3 9.5 7 4ZM3 9.5h18M9 9.5l3 10.5 3-10.5M7 4l2 5.5M17 4l-2 5.5',
  // Pulls to come: a star, and one more.
  warps:
    'M10.5 3c.9 4.4 3.1 6.6 7.5 7.5-4.4.9-6.6 3.1-7.5 7.5-.9-4.4-3.1-6.6-7.5-7.5 4.4-.9 6.6-3.1 7.5-7.5ZM18.5 15.5v5M16 18h5',
  // Pulls made: a clock running back.
  history: 'M12 7.5V12l3 2M3.5 12a8.5 8.5 0 1 0 2.7-6.2M3.5 4v4.5H8',
  // Speed: a lightning bolt.
  speed: 'M13 2.5 5 13.5h6l-1 8 8-11h-6l1-8Z',
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

export type ToolIconName = keyof typeof PATHS

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
      <path
        d={PATHS[name]}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
