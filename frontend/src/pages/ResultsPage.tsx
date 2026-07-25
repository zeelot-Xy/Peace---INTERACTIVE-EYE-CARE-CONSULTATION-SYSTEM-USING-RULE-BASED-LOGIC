import { AlertTriangle, ArrowLeft, BookOpen, Info, Printer, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'

import { PageError, PageLoading } from '../components/PageState'
import { api, apiErrorMessage } from '../lib/api'
import type { ApiEnvelope } from '../types/auth'
import type { ConsultationResult, KnowledgeItem } from '../types/consultation'

function ItemList({ items, empty, field = 'title' }: { items: KnowledgeItem[]; empty: string; field?: 'title' | 'possible_indication_label' }) {
  if (!items.length) return <p className="text-slate-600 dark:text-slate-300">{empty}</p>
  return (
    <ul className="grid gap-4">
      {items.map((item) => (
        <li className="rounded-2xl border border-slate-200 p-5 dark:border-slate-700" key={item.id ?? item.rule_id ?? item.title ?? item.name ?? item.risk_label}>
          <h3 className="font-bold">{item[field] ?? item.title ?? item.name ?? item.risk_label ?? 'Safety warning'}</h3>
          {item.message && <p className="mt-2 text-slate-700 dark:text-slate-200">{item.message}</p>}
          {item.summary && <p className="mt-2 text-slate-700 dark:text-slate-200">{item.summary}</p>}
          {item.explanation && <p className="mt-2 text-slate-700 dark:text-slate-200">{item.explanation}</p>}
          {item.limitations && <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{item.limitations}</p>}
        </li>
      ))}
    </ul>
  )
}

export function ResultsPage() {
  const { consultationId = '' } = useParams()
  const location = useLocation()
  const reportView = location.pathname.startsWith('/reports/')
  const [result, setResult] = useState<ConsultationResult | null>(null)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setError('')
    try {
      const response = await api.get<ApiEnvelope<{ result: ConsultationResult }>>(`/consultations/${consultationId}/result`)
      setResult(response.data.data?.result ?? null)
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }, [consultationId])

  useEffect(() => {
    api.get<ApiEnvelope<{ result: ConsultationResult }>>(`/consultations/${consultationId}/result`)
      .then((response) => setResult(response.data.data?.result ?? null))
      .catch((requestError) => setError(apiErrorMessage(requestError)))
  }, [consultationId])

  if (error) return <PageError message={error} retry={load} />
  if (!result) return <PageLoading message="Preparing your consultation guidance…" />

  const urgent = (result.overall_risk?.rank ?? 0) >= 3
  return (
    <main className="mx-auto max-w-5xl px-5 py-10 sm:px-6 sm:py-14">
      <div className="no-print mb-7 flex flex-wrap items-center justify-between gap-3">
        <Link className="inline-flex items-center gap-2 font-semibold text-slate-600 dark:text-slate-300" to="/history"><ArrowLeft aria-hidden="true" size={17} /> History</Link>
        <div className="flex gap-3">
          {!reportView && <Link className="rounded-xl border border-slate-300 px-4 py-2 font-semibold dark:border-slate-600" to={`/reports/${consultationId}`}>Report view</Link>}
          <button className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 font-semibold text-white dark:bg-white dark:text-slate-900" onClick={() => window.print()} type="button"><Printer aria-hidden="true" size={17} /> Print</button>
        </div>
      </div>

      <header>
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700 dark:text-teal-300">{reportView ? 'Consultation report' : 'Your consultation results'}</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight">Educational eye-care guidance</h1>
        <p className="mt-3 text-sm text-slate-500">Knowledge version {result.knowledge.content_version}</p>
      </header>

      <section className={`mt-8 rounded-3xl border-2 p-6 sm:p-8 ${urgent ? 'border-red-600 bg-red-50 text-red-950 dark:bg-red-950 dark:text-red-50' : 'border-teal-500 bg-teal-50 text-teal-950 dark:bg-teal-950 dark:text-teal-50'}`} aria-labelledby="risk-heading">
        <div className="flex items-start gap-4">
          {urgent ? <AlertTriangle aria-hidden="true" className="shrink-0" size={31} /> : <ShieldCheck aria-hidden="true" className="shrink-0" size={31} />}
          <div>
            <p className="text-sm font-bold uppercase tracking-wider">Recommended action level</p>
            <h2 className="mt-1 text-3xl font-bold" id="risk-heading">{result.overall_risk?.label ?? 'No specific pathway matched'}</h2>
            <p className="mt-3 text-lg font-medium">{result.overall_risk?.action_window ?? 'Arrange an eye examination if symptoms concern you, persist, or worsen.'}</p>
          </div>
        </div>
      </section>

      {result.red_flags.length > 0 && (
        <section className="mt-8" aria-labelledby="red-flags-heading">
          <h2 className="text-2xl font-bold" id="red-flags-heading">Important warning signs identified</h2>
          <ItemList empty="" items={result.red_flags} />
        </section>
      )}

      <div className="mt-10 grid gap-10 lg:grid-cols-2">
        <section aria-labelledby="recommendations-heading">
          <h2 className="mb-5 text-2xl font-bold" id="recommendations-heading">Recommended next steps</h2>
          <ItemList empty="No specific recommendation was generated. Seek professional advice if you remain concerned." items={result.recommendations} />
        </section>
        <section aria-labelledby="indications-heading">
          <h2 className="mb-2 text-2xl font-bold" id="indications-heading">Possible indications</h2>
          <p className="mb-5 text-sm text-slate-600 dark:text-slate-300">These are symptom patterns, not diagnoses.</p>
          <ItemList empty="Your answers did not match a named indication in this educational knowledge base." field="possible_indication_label" items={result.possible_indications} />
        </section>
      </div>

      <section className="mt-10 rounded-3xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900" aria-labelledby="explanation-heading">
        <div className="flex items-center gap-3"><Info aria-hidden="true" className="text-teal-700" /><h2 className="text-2xl font-bold" id="explanation-heading">Why this guidance appeared</h2></div>
        <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{result.match_score_notice}</p>
        {result.matched_rules.length ? (
          <ul className="mt-5 grid gap-3">
            {result.matched_rules.map((rule) => <li className="rounded-xl bg-slate-50 p-4 dark:bg-slate-800" key={rule.id ?? rule.rule_id ?? rule.name}><strong>{rule.name}</strong><p className="mt-1 text-sm">{rule.explanation ?? rule.rationale}</p></li>)}
          </ul>
        ) : <p className="mt-4">No complete authored rule matched all required criteria.</p>}
      </section>

      <section className="mt-8 rounded-3xl border border-slate-200 p-6 dark:border-slate-700" aria-labelledby="sources-heading">
        <div className="flex items-center gap-3"><BookOpen aria-hidden="true" className="text-teal-700" /><h2 className="text-2xl font-bold" id="sources-heading">Sources</h2></div>
        <ul className="mt-5 grid gap-3">
          {result.evidence.map((source) => (
            <li key={source.id}><a className="font-semibold text-teal-700 underline underline-offset-4 dark:text-teal-300" href={source.url} rel="noreferrer" target="_blank">{source.title}</a>{source.organization && <span className="text-slate-500"> — {source.organization}</span>}</li>
          ))}
        </ul>
      </section>

      <aside className="mt-8 rounded-2xl bg-slate-100 p-5 text-sm leading-6 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
        <strong>Important limitation:</strong> {result.disclaimer}
      </aside>
    </main>
  )
}
