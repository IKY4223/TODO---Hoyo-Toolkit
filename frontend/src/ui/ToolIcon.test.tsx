import { render } from '@testing-library/react'
import { expect, test } from 'vitest'
import { ToolIcon } from './ToolIcon'

test('a sign with lines cut out of it masks only itself, however often it shows', () => {
  const { container } = render(
    <>
      <ToolIcon name="builds" />
      <ToolIcon name="builds" />
    </>,
  )
  const masks = [...container.querySelectorAll('mask')].map((mask) => mask.id)
  const uses = [...container.querySelectorAll('g[mask]')].map((g) => g.getAttribute('mask'))
  expect(new Set(masks).size).toBe(2)
  expect(uses).toEqual(masks.map((id) => `url(#${id})`))
  expect(masks.every((id) => /^[\w-]+$/.test(id))).toBe(true)
})

test('a plain sign carries no mask', () => {
  const { container } = render(<ToolIcon name="relics" />)
  expect(container.querySelector('mask')).toBeNull()
})
