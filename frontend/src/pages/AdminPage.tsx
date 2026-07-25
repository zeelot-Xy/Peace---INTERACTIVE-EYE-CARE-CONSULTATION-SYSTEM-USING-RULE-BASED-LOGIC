import { Activity, BookOpenCheck, FileClock, LoaderCircle, ShieldCheck, Upload, Users } from 'lucide-react'
import { useEffect, useState } from 'react'

import { PageError, PageLoading } from '../components/PageState'
import { api, apiErrorMessage } from '../lib/api'
import type { AdminConsultation, AdminReport, AdminSummary, AuditItem, KnowledgeVersion } from '../types/admin'
import type { ApiEnvelope, User } from '../types/auth'

interface AdminData {
  summary: AdminSummary
  users: User[]
  consultations: AdminConsultation[]
  audits: AuditItem[]
  versions: KnowledgeVersion[]
}

export function AdminPage() {
  const [data, setData] = useState<AdminData | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [report, setReport] = useState<AdminReport | null>(null)

  async function load() {
    setError('')
    try {
      const [summary, users, consultations, audits, versions] = await Promise.all([
        api.get<ApiEnvelope<{ summary: AdminSummary }>>('/admin/summary'),
        api.get<ApiEnvelope<{ items: User[] }>>('/admin/users?per_page=10'),
        api.get<ApiEnvelope<{ items: AdminConsultation[] }>>('/admin/consultations?per_page=10'),
        api.get<ApiEnvelope<{ items: AuditItem[] }>>('/admin/audit-logs?per_page=12'),
        api.get<ApiEnvelope<{ items: KnowledgeVersion[] }>>('/admin/knowledge'),
      ])
      setData({
        summary: summary.data.data!.summary,
        users: users.data.data?.items ?? [],
        consultations: consultations.data.data?.items ?? [],
        audits: audits.data.data?.items ?? [],
        versions: versions.data.data?.items ?? [],
      })
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0)
    return () => window.clearTimeout(timer)
  }, [])

  async function validatePackage(event: React.FormEvent) {
    event.preventDefault()
    if (!file) return
    setBusy('upload')
    setError('')
    const form = new FormData()
    form.append('package', file)
    try {
      await api.post('/admin/knowledge/validate', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setFile(null)
      const input = document.querySelector<HTMLInputElement>('#knowledge-package')
      if (input) input.value = ''
      await load()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setBusy('')
    }
  }

  async function activate(version: KnowledgeVersion, rollback: boolean) {
    const verb = rollback ? 'roll back to' : 'publish'
    if (!window.confirm(`Confirm that you want to ${verb} ${version.package_id}?`)) return
    setBusy(version.id)
    setError('')
    try {
      await api.post(`/admin/knowledge/${version.id}/${rollback ? 'rollback' : 'publish'}`)
      await load()
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setBusy('')
    }
  }

  async function viewReport(id: string) {
    setBusy(`report-${id}`)
    try {
      const response = await api.get<ApiEnvelope<{ report: AdminReport }>>(`/admin/consultations/${id}/report`)
      setReport(response.data.data?.report ?? null)
    } catch (requestError) {
      setError(apiErrorMessage(requestError))
    } finally {
      setBusy('')
    }
  }

  if (error && !data) return <PageError message={error} retry={() => void load()} />
  if (!data) return <PageLoading message="Retrieving summaries, audit events, and knowledge versions." />

  const cards = [
    { label: 'Accounts', value: data.summary.users.total, detail: `${data.summary.users.patients} patients`, icon: Users },
    { label: 'Consultations', value: data.summary.consultations.total, detail: `${data.summary.consultations.completed} completed`, icon: Activity },
    { label: 'Stored reports', value: data.summary.reports, detail: 'PDF generation begins in Phase 9', icon: FileClock },
  ]

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Administrator workspace</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Operations and knowledge governance</h1>
      <p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-300">Review activity and validate complete knowledge packages. Publishing changes only future consultations; prior results remain tied to their stored version.</p>
      {error && <p className="mt-5 rounded-xl bg-red-50 p-4 text-red-800" role="alert">{error}</p>}

      <section aria-label="System summary" className="mt-8 grid gap-4 md:grid-cols-3">
        {cards.map(({ label, value, detail, icon: Icon }) => (
          <article className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900" key={label}>
            <Icon aria-hidden="true" className="text-teal-700 dark:text-teal-300" />
            <p className="mt-4 text-sm font-semibold text-slate-500">{label}</p>
            <p className="mt-1 text-3xl font-bold">{value}</p>
            <p className="mt-1 text-sm text-slate-500">{detail}</p>
          </article>
        ))}
      </section>

      <section className="admin-section" aria-labelledby="knowledge-heading">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div><h2 id="knowledge-heading" className="text-2xl font-bold">Knowledge versions</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">ZIP archives are validated and diffed before any publish action is available.</p></div>
          <form className="flex flex-wrap items-end gap-3" onSubmit={validatePackage}>
            <label className="text-sm font-semibold" htmlFor="knowledge-package">Complete package ZIP
              <input accept=".zip,application/zip" className="mt-1 block max-w-72 text-sm" id="knowledge-package" onChange={(event) => setFile(event.target.files?.[0] ?? null)} type="file" />
            </label>
            <button className="rounded-xl bg-teal-700 px-4 py-2 font-semibold text-white disabled:opacity-60" disabled={!file || busy === 'upload'} type="submit">
              {busy === 'upload' ? <LoaderCircle aria-label="Validating" className="animate-spin" /> : <span className="inline-flex items-center gap-2"><Upload aria-hidden="true" size={17} /> Validate</span>}
            </button>
          </form>
        </div>
        <div className="mt-6 grid gap-4">
          {data.versions.map((version) => (
            <article className="rounded-2xl border border-slate-200 p-5 dark:border-slate-700" key={version.id}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2"><h3 className="font-bold">{version.title ?? 'Invalid upload'}</h3><span className={`status status-${version.status}`}>{version.is_active ? 'Active' : version.status}</span></div>
                  <p className="mt-1 text-sm text-slate-500">{version.package_id ?? 'Package identity unavailable'} · {version.fingerprint?.slice(0, 12) ?? 'No fingerprint'}</p>
                </div>
                {version.is_valid && !version.is_active && (
                  <button className="rounded-xl border border-teal-700 px-4 py-2 text-sm font-bold text-teal-800 dark:text-teal-200" disabled={busy === version.id} onClick={() => void activate(version, version.status === 'retired')} type="button">
                    {version.status === 'retired' ? 'Roll back to version' : 'Publish version'}
                  </button>
                )}
              </div>
              {version.validation_report.issues.length > 0 && <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-red-700">{version.validation_report.issues.map((issue) => <li key={`${issue.location}-${issue.code}`}>{issue.location}: {issue.message}</li>)}</ul>}
              {version.diff_summary && (
                <details className="mt-4 text-sm">
                  <summary className="cursor-pointer font-semibold">Inspect differences and affected rules</summary>
                  {version.diff_summary.warnings.map((warning) => <p className="mt-3 rounded-lg bg-amber-50 p-3 text-amber-900" key={warning}>{warning}</p>)}
                  <p className="mt-3"><strong>Affected rules:</strong> {version.diff_summary.affected_rule_ids.join(', ') || 'None'}</p>
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">{Object.entries(version.diff_summary.collections).map(([name, item]) => <p key={name}><strong>{name}</strong>: {item.added.length} added, {item.changed.length} changed, {item.removed.length} removed</p>)}</div>
                </details>
              )}
            </article>
          ))}
        </div>
      </section>

      <section className="admin-section" aria-labelledby="consultations-heading">
        <h2 id="consultations-heading" className="text-2xl font-bold">Recent consultations</h2>
        <div className="mt-5 overflow-x-auto"><table className="admin-table"><thead><tr><th>Patient</th><th>Status</th><th>Risk</th><th>Version</th><th>Report</th></tr></thead><tbody>{data.consultations.map((item) => <tr key={item.id}><td>{item.patient.full_name}<span>{item.patient.email}</span></td><td>{item.status}</td><td>{item.risk?.label ?? 'Not completed'}</td><td>{item.knowledge_version ?? '—'}</td><td><button className="text-teal-700 underline" disabled={busy === `report-${item.id}`} onClick={() => void viewReport(item.id)} type="button">View snapshot</button></td></tr>)}</tbody></table></div>
        {report && <aside className="mt-5 rounded-2xl bg-slate-100 p-5 dark:bg-slate-800" aria-label="Consultation report snapshot"><div className="flex justify-between gap-4"><h3 className="font-bold">{report.patient.full_name} · {report.status}</h3><button onClick={() => setReport(null)} type="button">Close</button></div><p className="mt-2 text-sm">Knowledge: {report.knowledge.content_version} · {report.knowledge.fingerprint?.slice(0, 12)}</p><pre className="mt-4 max-h-80 overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(report.result, null, 2)}</pre></aside>}
      </section>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section className="admin-section mt-0" aria-labelledby="users-heading"><h2 id="users-heading" className="text-xl font-bold">Recent accounts</h2><ul className="mt-4 divide-y divide-slate-200 dark:divide-slate-700">{data.users.map((user) => <li className="flex justify-between gap-4 py-3" key={user.id}><span>{user.full_name}<small className="block text-slate-500">{user.email}</small></span><span className="status">{user.role}</span></li>)}</ul></section>
        <section className="admin-section mt-0" aria-labelledby="audit-heading"><h2 id="audit-heading" className="text-xl font-bold">Audit trail</h2><ul className="mt-4 divide-y divide-slate-200 dark:divide-slate-700">{data.audits.map((item) => <li className="py-3 text-sm" key={item.id}><span className="font-semibold">{item.action}</span><span className="block text-slate-500">{item.actor?.email ?? 'System'} · {new Date(item.created_at).toLocaleString()}</span></li>)}</ul></section>
      </div>

      <p className="mt-8 flex items-center gap-2 text-sm text-slate-500"><ShieldCheck aria-hidden="true" size={17} /> All knowledge actions are audited. This knowledge base remains an unvalidated academic prototype.</p>
      <p className="mt-2 flex items-center gap-2 text-sm text-slate-500"><BookOpenCheck aria-hidden="true" size={17} /> Previous versions remain available for historical results and controlled rollback.</p>
    </main>
  )
}
