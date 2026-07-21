import { ClipboardList, History, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'

import { useAuth } from '../context/auth-context'

export function DashboardPage() {
  const { user } = useAuth()
  return (
    <main className="mx-auto max-w-6xl px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Patient dashboard</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Hello, {user?.full_name}</h1>
      <p className="mt-3 max-w-2xl text-slate-600">Your account is ready. The guided consultation and history features arrive in their approved development phases.</p>
      <div className="mt-10 grid gap-5 md:grid-cols-3">
        <article className="rounded-2xl border border-slate-200 bg-white p-6"><ClipboardList className="text-teal-700" /><h2 className="mt-4 font-semibold">Consultation</h2><p className="mt-2 text-sm text-slate-600">Available after the consultation engine phase.</p></article>
        <article className="rounded-2xl border border-slate-200 bg-white p-6"><History className="text-teal-700" /><h2 className="mt-4 font-semibold">History</h2><p className="mt-2 text-sm text-slate-600">Secure consultation history will appear here.</p></article>
        <Link className="rounded-2xl border border-teal-200 bg-teal-50 p-6 hover:border-teal-400" to="/profile"><UserRound className="text-teal-700" /><h2 className="mt-4 font-semibold">Profile and security</h2><p className="mt-2 text-sm text-slate-600">Update your details, password, or active sessions.</p></Link>
      </div>
    </main>
  )
}
