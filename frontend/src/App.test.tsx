import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const apiMock = vi.hoisted(() => ({
  defaults: { baseURL: 'http://localhost:5000/api/v1' },
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

const administrator = {
  ...patient,
  id: 'admin-1',
  email: 'admin@example.com',
  full_name: 'System Administrator',
  role: 'admin' as const,
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

  it('generates an immutable PDF report and exposes its secure download', async () => {
    const result = {
      outcome_state: 'matched',
      completeness_state: 'complete',
      knowledge: { package_id: 'eye-care-en-1.0.0', content_version: '1.0.0', fingerprint: 'abc' },
      overall_risk: { id: 'risk_routine', label: 'Routine', rank: 1, action_window: 'Arrange routine care.' },
      matched_rules: [],
      pending_rules: [],
      possible_indications: [],
      recommendations: [],
      red_flags: [],
      missing_fact_ids: [],
      evidence: [],
      inference_trace: [],
      disclaimer: 'This is not a diagnosis.',
      match_score_notice: 'Scores describe authored criteria only.',
    }
    apiMock.get.mockImplementation((url: string) => Promise.resolve({
      data: { data: url === '/users/me' ? { user: patient } : { result }, errors: [] },
    }))
    apiMock.post.mockResolvedValue({
      data: {
        data: {
          report: {
            id: 'report-1',
            consultation_id: 'complete-1',
            filename: 'eye-care-report.pdf',
            content_type: 'application/pdf',
            sha256: 'abc123',
            generated_at: '2026-07-26T08:00:00Z',
            risk: result.overall_risk,
            knowledge_version: '1.0.0',
            download_url: '/api/v1/reports/report-1/download',
          },
        },
        errors: [],
      },
    })

    render(<MemoryRouter initialEntries={['/consultations/complete-1/results']}><App /></MemoryRouter>)
    fireEvent.click(await screen.findByRole('button', { name: /generate pdf/i }))

    await waitFor(() => expect(apiMock.post).toHaveBeenCalledWith('/consultations/complete-1/report'))
    expect(await screen.findByRole('link', { name: /download pdf/i })).toHaveAttribute(
      'href',
      'http://localhost:5000/api/v1/reports/report-1/download',
    )
    expect(screen.getByRole('status')).toHaveTextContent(/immutable pdf report is ready/i)
  })

  it('sends patient history filters to the API', async () => {
    apiMock.get.mockImplementation((url: string) => Promise.resolve({
      data: {
        data: url === '/users/me' ? { user: patient } : { items: [] },
        errors: [],
      },
    }))

    render(<MemoryRouter initialEntries={['/history']}><App /></MemoryRouter>)
    await screen.findByRole('heading', { name: /consultation history/i })
    fireEvent.change(screen.getByLabelText(/status/i), { target: { value: 'completed' } })
    fireEvent.change(screen.getByLabelText(/action level/i), { target: { value: 'risk_urgent' } })

    await waitFor(() => expect(apiMock.get).toHaveBeenCalledWith(
      '/consultations?per_page=50&status=completed&risk=risk_urgent',
    ))
  })

  it('renders administrator summaries and retained knowledge versions for administrators', async () => {
    apiMock.get.mockImplementation((url: string) => {
      const payloads: Record<string, unknown> = {
        '/users/me': { user: administrator },
        '/admin/summary': {
          summary: {
            users: { total: 4, patients: 3, administrators: 1 },
            consultations: { total: 2, in_progress: 1, completed: 1, cancelled: 0 },
            reports: 0,
          },
        },
        '/admin/users?per_page=10': { items: [administrator] },
        '/admin/consultations?per_page=10': { items: [] },
        '/admin/audit-logs?per_page=12': { items: [] },
        '/admin/knowledge': {
          items: [{
            id: 'version-1',
            package_id: 'eye-care-en-1.0.0',
            schema_version: '1.0.0',
            content_version: '1.0.0',
            fingerprint: 'abcdef1234567890',
            title: 'Adult English Eye-Care Consultation Knowledge Package',
            status: 'published',
            is_valid: true,
            is_active: true,
            validation_report: { valid: true, issues: [] },
            diff_summary: null,
            uploaded_at: '2026-07-26T00:00:00Z',
            published_at: '2026-07-26T00:00:00Z',
            retired_at: null,
          }],
        },
      }
      return Promise.resolve({ data: { data: payloads[url], errors: [] } })
    })

    render(<MemoryRouter initialEntries={['/admin']}><App /></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: /operations and knowledge governance/i })).toBeInTheDocument()
    expect(await screen.findByText(/adult english eye-care consultation knowledge package/i)).toBeInTheDocument()
    expect(screen.getByText(/previous versions remain available/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /admin/i })).toBeInTheDocument()
  })

  it('redirects patients away from the administrator workspace', async () => {
    apiMock.get.mockImplementation((url: string) => Promise.resolve({
      data: {
        data: url === '/users/me' ? { user: patient } : { items: [] },
        errors: [],
      },
    }))

    render(<MemoryRouter initialEntries={['/admin']}><App /></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: /hello, test patient/i })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /operations and knowledge governance/i })).not.toBeInTheDocument()
  })
})
