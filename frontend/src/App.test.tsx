import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
}))

vi.mock('./lib/api', () => ({
  api: apiMock,
  apiErrorMessage: () => 'The request could not be completed.',
}))

const patient = {
  id: 'patient-1',
  email: 'patient@example.com',
  full_name: 'Test Patient',
  role: 'patient',
  is_active: true,
  phone: null,
  date_of_birth: null,
  created_at: '2026-07-13T00:00:00Z',
}

describe('App authentication experience', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockRejectedValue(new Error('not authenticated'))
  })

  it('presents the educational safety boundary on the landing page', async () => {
    render(<MemoryRouter><App /></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: /clear guidance through transparent rule-based reasoning/i })).toBeInTheDocument()
    expect(screen.getByText(/educational support, not a diagnosis/i)).toBeInTheDocument()
    expect(screen.getByText(/sudden vision loss/i)).toBeInTheDocument()
  })

  it('redirects an unauthenticated dashboard request to login', async () => {
    render(<MemoryRouter initialEntries={['/dashboard']}><App /></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: /sign in/i })).toBeInTheDocument()
  })

  it('validates registration fields before sending a request', async () => {
    render(<MemoryRouter initialEntries={['/register']}><App /></MemoryRouter>)
    await screen.findByRole('heading', { name: /create your account/i })
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))

    expect(await screen.findByText(/enter your full name/i)).toBeInTheDocument()
    expect(apiMock.post).not.toHaveBeenCalled()
  })

  it('logs in and displays the protected dashboard', async () => {
    apiMock.post.mockResolvedValue({ data: { data: { user: patient }, errors: [] } })
    render(<MemoryRouter initialEntries={['/login']}><App /></MemoryRouter>)
    await screen.findByRole('heading', { name: /sign in/i })
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: patient.email } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'a secure test password' } })
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => expect(screen.getByRole('heading', { name: /hello, test patient/i })).toBeInTheDocument())
    expect(apiMock.post).toHaveBeenCalledWith('/auth/login', {
      email: patient.email,
      password: 'a secure test password',
    })
  })

  it('restores a session and updates the patient profile', async () => {
    apiMock.get.mockResolvedValue({ data: { data: { user: patient }, errors: [] } })
    apiMock.patch.mockResolvedValue({ data: { data: { user: patient }, errors: [] } })
    render(<MemoryRouter initialEntries={['/profile']}><App /></MemoryRouter>)
    await screen.findByRole('heading', { name: /profile and security/i })
    fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'Updated Patient' } })
    fireEvent.click(screen.getByRole('button', { name: /save profile/i }))

    await waitFor(() => expect(apiMock.patch).toHaveBeenCalledWith('/users/me', {
      full_name: 'Updated Patient',
      phone: null,
      date_of_birth: null,
    }))
  })

  it('signs an authenticated user out from the header', async () => {
    apiMock.get.mockResolvedValue({ data: { data: { user: patient }, errors: [] } })
    apiMock.post.mockResolvedValue({ data: { data: { message: 'Signed out' }, errors: [] } })
    render(<MemoryRouter initialEntries={['/dashboard']}><App /></MemoryRouter>)
    await screen.findByRole('heading', { name: /hello, test patient/i })
    fireEvent.click(screen.getByRole('button', { name: /sign out/i }))

    await waitFor(() => expect(apiMock.post).toHaveBeenCalledWith('/auth/logout'))
  })
})
