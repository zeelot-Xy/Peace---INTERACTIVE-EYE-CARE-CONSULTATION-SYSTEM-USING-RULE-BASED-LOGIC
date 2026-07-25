import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
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

  it('presents one consultation question at a time and autosaves an answer', async () => {
    const consultation = {
      id: 'consultation-1',
      status: 'in_progress',
      revision: 0,
      knowledge: { package_id: 'eye-care-en-1.0.0', content_version: '1.0.0', fingerprint: 'abc' },
      progress: { resolved: 0, total_applicable: 36, percentage: 0 },
      next_question: {
        id: 'question_age_years',
        fact_id: 'fact_age_years',
        prompt: 'What is your age in completed years?',
        help_text: 'Adults only.',
        answer_type: 'integer',
        required: true,
        safety_critical: false,
        options: [],
        citation_ids: ['source-1'],
      },
      answers: [],
      skipped_question_ids: [],
      safety_alert: null,
      created_at: '2026-07-25T00:00:00Z',
      updated_at: '2026-07-25T00:00:00Z',
      completed_at: null,
      cancelled_at: null,
    }
    apiMock.get.mockImplementation((url: string) => Promise.resolve({
      data: { data: url === '/users/me' ? { user: patient } : { consultation }, errors: [] },
    }))
    apiMock.put.mockResolvedValue({
      data: { data: { consultation: { ...consultation, revision: 1, progress: { resolved: 1, total_applicable: 36, percentage: 2.78 }, next_question: { ...consultation.next_question, id: 'question_sudden_vision_loss', prompt: 'Have you suddenly lost vision?', answer_type: 'yes_no', safety_critical: true } } }, errors: [] },
    })

    render(<MemoryRouter initialEntries={['/consultations/consultation-1']}><App /></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: /what is your age/i })).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText(/age in completed years/i), { target: { value: '32' } })
    fireEvent.click(screen.getByRole('button', { name: /save and continue/i }))

    await waitFor(() => expect(apiMock.put).toHaveBeenCalledWith(
      '/consultations/consultation-1/responses/question_age_years',
      { answer: 32, skip: false, revision: 0 },
    ))
    expect(await screen.findByRole('heading', { name: /suddenly lost vision/i })).toBeInTheDocument()
  })

  it('shows urgent partial-inference advice prominently', async () => {
    const urgentConsultation = {
      id: 'urgent-1',
      status: 'in_progress',
      revision: 4,
      knowledge: { package_id: 'eye-care-en-1.0.0', content_version: '1.0.0', fingerprint: 'abc' },
      progress: { resolved: 4, total_applicable: 36, percentage: 11.11 },
      next_question: null,
      answers: [],
      skipped_question_ids: [],
      safety_alert: {
        requires_immediate_action: true,
        risk: { id: 'risk_emergency', label: 'Emergency', rank: 4, action_window: 'Seek emergency eye care now.' },
        red_flags: [],
        recommendations: [{ id: 'recommendation_emergency', message: 'Do not wait for a routine appointment.' }],
        disclaimer: 'Educational support only.',
      },
      created_at: '2026-07-25T00:00:00Z',
      updated_at: '2026-07-25T00:00:00Z',
      completed_at: null,
      cancelled_at: null,
    }
    apiMock.get.mockImplementation((url: string) => Promise.resolve({
      data: { data: url === '/users/me' ? { user: patient } : { consultation: urgentConsultation }, errors: [] },
    }))

    render(<MemoryRouter initialEntries={['/consultations/urgent-1']}><App /></MemoryRouter>)
    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/seek emergency eye care now/i)
    expect(alert).toHaveTextContent(/do not wait/i)
  })

  it('keeps possible indications visually and verbally separate from diagnoses', async () => {
    const result = {
      outcome_state: 'matched',
      completeness_state: 'complete',
      knowledge: { package_id: 'eye-care-en-1.0.0', content_version: '1.0.0', fingerprint: 'abc' },
      overall_risk: { id: 'risk_prompt', label: 'Prompt assessment', rank: 2, action_window: 'Arrange professional assessment promptly.' },
      matched_rules: [],
      pending_rules: [],
      possible_indications: [{ id: 'condition_dry_eye', possible_indication_label: 'Symptoms consistent with a possible dry-eye pattern', summary: 'A symptom pattern.', limitations: 'Other causes are possible.' }],
      recommendations: [{ id: 'recommendation_prompt', title: 'Prompt eye examination', message: 'Arrange an eye examination.' }],
      red_flags: [{ rule_id: 'rule-warning', risk_label: 'Same-day urgent', explanation: 'A safety warning matched the provided answers.' }],
      missing_fact_ids: [],
      evidence: [{ id: 'source-nei', title: 'Dry Eye', organization: 'National Eye Institute', url: 'https://example.test/source' }],
      inference_trace: [],
      disclaimer: 'This is not a diagnosis.',
      match_score_notice: 'Scores describe authored criteria only.',
    }
    apiMock.get.mockImplementation((url: string) => Promise.resolve({
      data: { data: url === '/users/me' ? { user: patient } : { result }, errors: [] },
    }))

    render(<MemoryRouter initialEntries={['/consultations/complete-1/results']}><App /></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: /possible indications/i })).toBeInTheDocument()
    expect(screen.getByText(/these are symptom patterns, not diagnoses/i)).toBeInTheDocument()
    expect(screen.getByText(/a safety warning matched/i)).toBeInTheDocument()
    expect(screen.getByText(/this is not a diagnosis/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /dry eye/i })).toHaveAttribute('target', '_blank')
  })
})
