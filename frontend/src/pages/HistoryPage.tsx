import { CalendarDays, ChevronRight, ClipboardList, Filter } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { PageError, PageLoading } from '../components/PageState'
import { api, apiErrorMessage } from '../lib/api'
import type { ApiEnvelope } from '../types/auth'
import type { ConsultationStatus, HistoryItem } from '../types/consultation'

const statusLabels: Record<ConsultationStatus, string> = {
  in_progress: 'In progress',
  completed: 'Completed',
  cancelled: 'Cancelled',
}

function historyUrl(status: 'all' | ConsultationStatus, risk: string, dateFrom: string, dateTo: string) {
  const query = new URLSearchParams({ per_page: '50' })
  if (status !== 'all') query.set('status', status)
  if (risk !== 'all') query.set('risk', risk)
  if (dateFrom) query.set('date_from', dateFrom)
  if (dateTo) query.set('date_to', dateTo)
  return `/consultations?${query}`
}

export function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[] | null>(null)
  const [status, setStatus] = useState<'all' | ConsultationStatus>('all')
  const [risk, setRisk] = useState('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      const response = await api.get<ApiEnvelope<{ items: HistoryItem[] }>>(historyUrl(status, risk, dateFrom, dateTo))
      setError('')
      setItems(response.data.data?.items ?? [])
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }, [dateFrom, dateTo, risk, status])

  useEffect(() => {
    api.get<ApiEnvelope<{ items: HistoryItem[] }>>(historyUrl(status, risk, dateFrom, dateTo))
      .then((response) => {
        setError('')
        setItems(response.data.data?.items ?? [])
      })
      .catch((requestError) => setError(apiErrorMessage(requestError)))
  }, [dateFrom, dateTo, risk, status])

  if (error) return <PageError message={error} retry={load} />
  if (!items) return <PageLoading message="Loading your consultation history…" />

  return (
    <main className="mx-auto max-w-5xl px-6 py-14">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700 dark:text-teal-300">Your records</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Consultation history</h1>
      <p className="mt-3 text-slate-600 dark:text-slate-300">Resume saved consultations or revisit immutable completed guidance.</p>

      <section aria-label="History filters" className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
        <div className="mb-4 flex items-center gap-2 font-semibold">
          <Filter aria-hidden="true" size={18} /> Filter records
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <label className="grid gap-1 text-sm font-medium">Status
            <select className="rounded-xl border border-slate-300 bg-white px-3 py-2 dark:border-slate-600 dark:bg-slate-950" onChange={(event) => setStatus(event.target.value as typeof status)} value={status}>
              <option value="all">All statuses</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium">Action level
            <select className="rounded-xl border border-slate-300 bg-white px-3 py-2 dark:border-slate-600 dark:bg-slate-950" onChange={(event) => setRisk(event.target.value)} value={risk}>
              <option value="all">All levels</option>
              <option value="risk_routine">Routine</option>
              <option value="risk_prompt">Prompt assessment</option>
              <option value="risk_urgent">Same-day urgent</option>
              <option value="risk_emergency">Emergency</option>
            </select>
          </label>
          <label className="grid gap-1 text-sm font-medium">From
            <input className="rounded-xl border border-slate-300 bg-white px-3 py-2 dark:border-slate-600 dark:bg-slate-950" onChange={(event) => setDateFrom(event.target.value)} type="date" value={dateFrom} />
          </label>
          <label className="grid gap-1 text-sm font-medium">To
            <input className="rounded-xl border border-slate-300 bg-white px-3 py-2 dark:border-slate-600 dark:bg-slate-950" min={dateFrom || undefined} onChange={(event) => setDateTo(event.target.value)} type="date" value={dateTo} />
          </label>
        </div>
      </section>

      {items.length === 0 ? (
        <section className="mt-8 rounded-3xl border border-dashed border-slate-300 p-10 text-center dark:border-slate-700">
          <ClipboardList className="mx-auto text-slate-400" size={36} />
          <h2 className="mt-4 text-xl font-bold">No consultations in this view</h2>
          <p className="mt-2 text-slate-600 dark:text-slate-300">Change the filters or start a consultation from your dashboard.</p>
          <Link className="mt-5 inline-block font-semibold text-teal-700 dark:text-teal-300" to="/dashboard">Go to dashboard</Link>
        </section>
      ) : (
        <ul className="mt-8 grid gap-4">
          {items.map((item) => {
            const destination = item.status === 'completed' ? `/consultations/${item.id}/results` : `/consultations/${item.id}`
            return (
              <li key={item.id}>
                <Link className="group flex items-center gap-5 rounded-2xl border border-slate-200 bg-white p-5 hover:border-teal-400 hover:shadow-sm dark:border-slate-700 dark:bg-slate-900" to={destination}>
                  <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-slate-100 text-teal-700 dark:bg-slate-800 dark:text-teal-300"><CalendarDays aria-hidden="true" /></span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-bold">{new Date(item.created_at).toLocaleDateString()}</h2>
                      <span className={`status status-${item.status}`}>{statusLabels[item.status]}</span>
                      {item.risk?.label && <span className="text-sm font-semibold text-slate-600 dark:text-slate-300">{item.risk.label}</span>}
                    </div>
                    <p className="mt-1 truncate text-sm text-slate-500">Knowledge version {item.knowledge_version}</p>
                    {item.report_id && <p className="mt-1 text-xs font-semibold text-teal-700 dark:text-teal-300">PDF report ready</p>}
                  </div>
                  {item.status !== 'cancelled' && <ChevronRight aria-hidden="true" className="text-slate-400 group-hover:text-teal-700" />}
                </Link>
              </li>
            )
          })}
        </ul>
      )}
    </main>
  )
}
