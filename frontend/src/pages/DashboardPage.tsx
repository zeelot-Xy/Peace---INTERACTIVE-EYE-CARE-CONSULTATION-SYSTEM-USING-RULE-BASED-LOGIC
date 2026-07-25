import { ArrowRight, ClipboardList, History, LoaderCircle, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/auth-context'
import { api, apiErrorMessage } from '../lib/api'
import type { ApiEnvelope } from '../types/auth'
import type { Consultation, HistoryItem } from '../types/consultation'

export function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [history, setHistory] = useState<HistoryItem[] | null>(null)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get<ApiEnvelope<{ items: HistoryItem[] }>>('/consultations?per_page=5')
      .then((response) => setHistory(response.data.data?.items ?? []))
      .catch(() => setHistory([]))
  }, [])

  async function startConsultation() {
    setStarting(true)
    setError('')
    try {
      const response = await api.post<ApiEnvelope<{ consultation: Consultation }>>('/consultations')
      const consultation = response.data.data?.consultation
      if (consultation) navigate(`/consultations/${consultation.id}`)
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
      setStarting(false)
    }
  }

  const active = history?.find((item) => item.status === 'in_progress')
  return (
    <main className="mx-auto max-w-6xl px-6 py-14">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Patient dashboard</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Hello, {user?.full_name}</h1>
      <p className="mt-3 max-w-2xl text-slate-600 dark:text-slate-300">Use the guided questions to understand an appropriate level of eye care. This system does not provide a diagnosis.</p>
      {error && <p className="mt-5 rounded-xl bg-red-50 p-4 text-red-800" role="alert">{error}</p>}

      <section className="mt-9 overflow-hidden rounded-3xl bg-gradient-to-br from-teal-800 to-cyan-700 p-7 text-white shadow-lg sm:p-9">
        <div className="max-w-2xl">
          <ClipboardList aria-hidden="true" size={30} />
          <h2 className="mt-5 text-3xl font-bold">{active ? 'Continue where you stopped' : 'Start an eye-care consultation'}</h2>
          <p className="mt-3 text-teal-50">{active ? 'Your answers were saved securely. Resume the next applicable question.' : 'Answer one clear question at a time. Urgent warning signs are highlighted immediately.'}</p>
          {active ? (
            <Link className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-bold text-teal-900" to={`/consultations/${active.id}`}>Resume consultation <ArrowRight aria-hidden="true" size={18} /></Link>
          ) : (
            <button className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-bold text-teal-900 disabled:opacity-70" disabled={starting} onClick={startConsultation} type="button">
              {starting ? <><LoaderCircle className="animate-spin" size={18} /> Starting…</> : <>Begin consultation <ArrowRight aria-hidden="true" size={18} /></>}
            </button>
          )}
        </div>
      </section>

      <div className="mt-7 grid gap-5 md:grid-cols-2">
        <Link className="rounded-2xl border border-slate-200 bg-white p-6 hover:border-teal-400 dark:border-slate-700 dark:bg-slate-900" to="/history"><History className="text-teal-700 dark:text-teal-300" /><h2 className="mt-4 font-semibold">Consultation history</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{history === null ? 'Loading recent consultations…' : history.length ? `${history.length} recent consultation${history.length === 1 ? '' : 's'}` : 'No consultations recorded yet.'}</p></Link>
        <Link className="rounded-2xl border border-slate-200 bg-white p-6 hover:border-teal-400 dark:border-slate-700 dark:bg-slate-900" to="/profile"><UserRound className="text-teal-700 dark:text-teal-300" /><h2 className="mt-4 font-semibold">Profile and security</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Update your details, password, or active sessions.</p></Link>
      </div>
    </main>
  )
}
