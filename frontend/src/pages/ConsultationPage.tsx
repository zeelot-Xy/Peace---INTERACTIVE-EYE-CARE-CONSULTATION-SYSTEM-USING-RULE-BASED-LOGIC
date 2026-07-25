import { AlertTriangle, ArrowLeft, Check, ChevronRight, ShieldAlert, Trash2 } from 'lucide-react'
import { FormEvent, useCallback, useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'

import { PageError, PageLoading } from '../components/PageState'
import { api, apiErrorMessage } from '../lib/api'
import type { ApiEnvelope } from '../types/auth'
import type { Consultation, ConsultationQuestion } from '../types/consultation'

function answerLabel(answer: boolean | number | string) {
  if (answer === true) return 'Yes'
  if (answer === false) return 'No'
  return String(answer)
}

function AnswerControl({
  question,
  value,
  onChange,
}: {
  question: ConsultationQuestion
  value: string
  onChange: (value: string) => void
}) {
  if (question.answer_type === 'yes_no') {
    return (
      <fieldset>
        <legend className="sr-only">{question.prompt}</legend>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
            ['true', 'Yes'],
            ['false', 'No'],
          ].map(([optionValue, label]) => (
            <label className={`answer-option ${value === optionValue ? 'answer-option-selected' : ''}`} key={optionValue}>
              <input checked={value === optionValue} className="sr-only" name="answer" onChange={() => onChange(optionValue)} type="radio" />
              <span>{label}</span>
              {value === optionValue && <Check aria-hidden="true" size={20} />}
            </label>
          ))}
        </div>
      </fieldset>
    )
  }

  if (question.answer_type === 'single_choice') {
    return (
      <fieldset className="grid gap-3">
        <legend className="sr-only">{question.prompt}</legend>
        {question.options.map((option) => (
          <label className={`answer-option ${value === option.value ? 'answer-option-selected' : ''}`} key={option.value}>
            <input checked={value === option.value} className="sr-only" name="answer" onChange={() => onChange(option.value)} type="radio" />
            <span>{option.label}</span>
            {value === option.value && <Check aria-hidden="true" size={20} />}
          </label>
        ))}
      </fieldset>
    )
  }

  return (
    <div>
      <label className="mb-2 block text-sm font-semibold" htmlFor="integer-answer">Age in completed years</label>
      <input
        className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-lg dark:border-slate-600 dark:bg-slate-900"
        id="integer-answer"
        inputMode="numeric"
        max={120}
        min={18}
        onChange={(event) => onChange(event.target.value)}
        required
        type="number"
        value={value}
      />
    </div>
  )
}

export function ConsultationPage() {
  const { consultationId = '' } = useParams()
  const navigate = useNavigate()
  const [consultation, setConsultation] = useState<Consultation | null>(null)
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [saving, setSaving] = useState(false)
  const [confirmCancel, setConfirmCancel] = useState(false)

  const load = useCallback(async () => {
    setError('')
    try {
      const response = await api.get<ApiEnvelope<{ consultation: Consultation }>>(`/consultations/${consultationId}`)
      setConsultation(response.data.data?.consultation ?? null)
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }, [consultationId])

  useEffect(() => {
    api.get<ApiEnvelope<{ consultation: Consultation }>>(`/consultations/${consultationId}`)
      .then((response) => setConsultation(response.data.data?.consultation ?? null))
      .catch((requestError) => setError(apiErrorMessage(requestError)))
  }, [consultationId])

  async function submitAnswer(event: FormEvent) {
    event.preventDefault()
    if (!consultation?.next_question || answer === '') {
      setNotice('Choose or enter an answer before continuing.')
      return
    }
    setSaving(true)
    setNotice('')
    try {
      const parsedAnswer =
        consultation.next_question.answer_type === 'yes_no'
          ? answer === 'true'
          : consultation.next_question.answer_type === 'integer'
            ? Number(answer)
            : answer
      const response = await api.put<ApiEnvelope<{ consultation: Consultation }>>(
        `/consultations/${consultation.id}/responses/${consultation.next_question.id}`,
        { answer: parsedAnswer, skip: false, revision: consultation.revision },
      )
      setConsultation(response.data.data?.consultation ?? consultation)
      setAnswer('')
    } catch (requestError) {
      setNotice(apiErrorMessage(requestError))
      if ((requestError as { response?: { status?: number } }).response?.status === 409) await load()
    } finally {
      setSaving(false)
    }
  }

  async function skipQuestion() {
    if (!consultation?.next_question) return
    setSaving(true)
    try {
      const response = await api.put<ApiEnvelope<{ consultation: Consultation }>>(
        `/consultations/${consultation.id}/responses/${consultation.next_question.id}`,
        { skip: true, revision: consultation.revision },
      )
      setConsultation(response.data.data?.consultation ?? consultation)
      setAnswer('')
    } catch (requestError) {
      setNotice(apiErrorMessage(requestError))
    } finally {
      setSaving(false)
    }
  }

  async function revise(questionId: string) {
    if (!consultation) return
    setSaving(true)
    try {
      const response = await api.delete<ApiEnvelope<{ consultation: Consultation }>>(
        `/consultations/${consultation.id}/responses/${questionId}`,
        { data: { revision: consultation.revision } },
      )
      setConsultation(response.data.data?.consultation ?? consultation)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (requestError) {
      setNotice(apiErrorMessage(requestError))
    } finally {
      setSaving(false)
    }
  }

  async function complete() {
    if (!consultation) return
    setSaving(true)
    try {
      await api.post(`/consultations/${consultation.id}/complete`, { revision: consultation.revision })
      navigate(`/consultations/${consultation.id}/results`)
    } catch (requestError) {
      setNotice(apiErrorMessage(requestError))
      await load()
    } finally {
      setSaving(false)
    }
  }

  async function cancel() {
    if (!consultation) return
    setSaving(true)
    try {
      await api.post(`/consultations/${consultation.id}/cancel`, { revision: consultation.revision })
      navigate('/history', { replace: true })
    } catch (requestError) {
      setNotice(apiErrorMessage(requestError))
    } finally {
      setSaving(false)
    }
  }

  if (error) return <PageError message={error} retry={load} />
  if (!consultation) return <PageLoading message="Restoring your consultation…" />
  if (consultation.status === 'completed') return <Navigate replace to={`/consultations/${consultation.id}/results`} />
  if (consultation.status === 'cancelled') {
    return <PageError message="This consultation was cancelled and cannot be changed." />
  }

  const question = consultation.next_question
  return (
    <main className="mx-auto max-w-5xl px-5 py-10 sm:px-6 sm:py-14">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-teal-700 dark:text-slate-300" to="/dashboard">
          <ArrowLeft aria-hidden="true" size={17} /> Save and leave
        </Link>
        <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800 dark:bg-teal-950 dark:text-teal-200">
          Saved automatically
        </span>
      </div>

      {consultation.safety_alert && (
        <section className="mb-7 rounded-3xl border-2 border-red-600 bg-red-50 p-6 text-red-950 shadow-lg dark:bg-red-950 dark:text-red-50" role="alert">
          <div className="flex gap-4">
            <ShieldAlert aria-hidden="true" className="shrink-0" size={30} />
            <div>
              <p className="text-sm font-bold uppercase tracking-wider">{consultation.safety_alert.risk.label}</p>
              <h1 className="mt-1 text-2xl font-bold">{consultation.safety_alert.risk.action_window}</h1>
              {consultation.safety_alert.recommendations.map((item) => (
                <p className="mt-3 font-medium" key={item.id}>{item.message}</p>
              ))}
            </div>
          </div>
        </section>
      )}

      <section aria-label="Consultation progress">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700 dark:text-teal-300">Guided consultation</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              {consultation.progress.resolved} of {consultation.progress.total_applicable} applicable questions answered
            </p>
          </div>
          <span className="text-lg font-bold">{Math.round(consultation.progress.percentage)}%</span>
        </div>
        <div aria-label={`${Math.round(consultation.progress.percentage)}% complete`} aria-valuemax={100} aria-valuemin={0} aria-valuenow={consultation.progress.percentage} className="mt-3 h-3 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700" role="progressbar">
          <div className="h-full rounded-full bg-teal-600 transition-[width]" style={{ width: `${consultation.progress.percentage}%` }} />
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-9 dark:border-slate-700 dark:bg-slate-900">
        {question ? (
          <form onSubmit={submitAnswer}>
            {question.safety_critical && (
              <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-950">
                <AlertTriangle aria-hidden="true" size={15} /> Important safety question
              </p>
            )}
            <h1 className="max-w-3xl text-2xl font-bold leading-tight sm:text-4xl">{question.prompt}</h1>
            {question.help_text && <p className="mt-3 text-slate-600 dark:text-slate-300">{question.help_text}</p>}
            <div className="mt-8"><AnswerControl onChange={setAnswer} question={question} value={answer} /></div>
            {notice && <p className="mt-5 rounded-xl bg-amber-50 p-3 text-sm text-amber-950 dark:bg-amber-950 dark:text-amber-100" role="alert">{notice}</p>}
            <div className="mt-8 flex flex-wrap gap-3">
              <button className="inline-flex items-center gap-2 rounded-xl bg-teal-700 px-6 py-3 font-bold text-white hover:bg-teal-800 disabled:opacity-60" disabled={saving} type="submit">
                {saving ? 'Saving…' : 'Save and continue'} <ChevronRight aria-hidden="true" size={18} />
              </button>
              {!question.required && !question.safety_critical && (
                <button className="rounded-xl px-5 py-3 font-semibold text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" disabled={saving} onClick={skipQuestion} type="button">Skip this question</button>
              )}
            </div>
          </form>
        ) : (
          <div className="text-center">
            <span className="mx-auto grid size-14 place-items-center rounded-full bg-emerald-100 text-emerald-800"><Check aria-hidden="true" /></span>
            <h1 className="mt-5 text-3xl font-bold">Your answers are complete</h1>
            <p className="mx-auto mt-3 max-w-xl text-slate-600 dark:text-slate-300">Generate your educational guidance now. Your result will remain tied to this knowledge version.</p>
            {notice && <p className="mt-5 text-red-700" role="alert">{notice}</p>}
            <button className="mt-7 rounded-xl bg-teal-700 px-7 py-3 font-bold text-white disabled:opacity-60" disabled={saving} onClick={complete} type="button">
              {saving ? 'Preparing results…' : 'View my results'}
            </button>
          </div>
        )}
      </section>

      {consultation.answers.length > 0 && (
        <details className="mt-7 rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
          <summary className="cursor-pointer font-bold">Review previous answers ({consultation.answers.length})</summary>
          <ul className="mt-4 divide-y divide-slate-200 dark:divide-slate-700">
            {consultation.answers.map((item) => (
              <li className="flex items-start justify-between gap-4 py-4" key={item.question_id}>
                <div><p className="font-medium">{item.question.prompt}</p><p className="mt-1 text-sm text-slate-600 dark:text-slate-300">Your answer: {answerLabel(item.answer)}</p></div>
                <button className="shrink-0 text-sm font-semibold text-teal-700 dark:text-teal-300" disabled={saving} onClick={() => revise(item.question_id)} type="button">Revise</button>
              </li>
            ))}
          </ul>
        </details>
      )}

      <section className="mt-8 border-t border-slate-200 pt-6 dark:border-slate-700">
        {confirmCancel ? (
          <div className="flex flex-wrap items-center gap-3" role="alert">
            <p className="mr-auto font-semibold">Cancel this consultation permanently?</p>
            <button className="rounded-xl bg-red-700 px-4 py-2 font-semibold text-white" disabled={saving} onClick={cancel} type="button">Yes, cancel</button>
            <button className="rounded-xl border border-slate-300 px-4 py-2 font-semibold" onClick={() => setConfirmCancel(false)} type="button">Keep consultation</button>
          </div>
        ) : (
          <button className="inline-flex items-center gap-2 text-sm font-semibold text-red-700 dark:text-red-300" onClick={() => setConfirmCancel(true)} type="button">
            <Trash2 aria-hidden="true" size={16} /> Cancel consultation
          </button>
        )}
      </section>
    </main>
  )
}
