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

export function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[] | null>(null)
  const [filter, setFilter] = useState<'all' | ConsultationStatus>('all')
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setError('')
    try {
      const response = await api.get<ApiEnvelope<{ items: HistoryItem[] }>>('/consultations?per_page=50')
      setItems(response.data.data?.items ?? [])
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }, [])

  useEffect(() => {
    api.get<ApiEnvelope<{ items: HistoryItem[] }>>('/consultations?per_page=50')
      .then((response) => setItems(response.data.data?.items ?? []))
      .catch((requestError) => setError(apiErrorMessage(requestError)))
  }, [])

  if (error) return <PageError message={error} retry={load} />
  if (!items) return <PageLoading message="Loading your consultation history…" />

  const visible = filter === 'all' ? items : items.filter((item) => item.status === filter)
  return (
    <main className="mx-auto max-w-5xl px-6 py-14">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700 dark:text-teal-300">Your records</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Consultation history</h1>
      <p className="mt-3 text-slate-600 dark:text-slate-300">Resume saved consultations or revisit immutable completed guidance.</p>

      <div className="mt-8 flex items-center gap-3">
        <Filter aria-hidden="true" size={18} />
        <label className="sr-only" htmlFor="history-filter">Filter consultations</label>
        <select className="rounded-xl border border-slate-300 bg-white px-4 py-2 dark:border-slate-600 dark:bg-slate-900" id="history-filter" onChange={(event) => setFilter(event.target.value as typeof filter)} value={filter}>
          <option value="all">All statuses</option>
          <option value="in_progress">In progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {visible.length === 0 ? (
        <section className="mt-8 rounded-3xl border border-dashed border-slate-300 p-10 text-center dark:border-slate-700">
          <ClipboardList className="mx-auto text-slate-400" size={36} />
          <h2 className="mt-4 text-xl font-bold">No consultations in this view</h2>
          <p className="mt-2 text-slate-600 dark:text-slate-300">Start a consultation from your dashboard whenever you are ready.</p>
          <Link className="mt-5 inline-block font-semibold text-teal-700 dark:text-teal-300" to="/dashboard">Go to dashboard</Link>
        </section>
      ) : (
        <ul className="mt-8 grid gap-4">
          {visible.map((item) => {
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
