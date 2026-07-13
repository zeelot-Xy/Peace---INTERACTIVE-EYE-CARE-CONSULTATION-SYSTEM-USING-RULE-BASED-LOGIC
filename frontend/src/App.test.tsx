import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('App', () => {
  it('presents the educational safety boundary on the landing page', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    )

    expect(
      screen.getByRole('heading', {
        name: /clear guidance through transparent rule-based reasoning/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getByText(/educational support, not a diagnosis/i)).toBeInTheDocument()
    expect(screen.getByText(/sudden vision loss/i)).toBeInTheDocument()
  })

  it('renders the about page through the router', () => {
    render(
      <MemoryRouter initialEntries={['/about']}>
        <App />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: /a careful educational tool/i })).toBeInTheDocument()
  })
})

