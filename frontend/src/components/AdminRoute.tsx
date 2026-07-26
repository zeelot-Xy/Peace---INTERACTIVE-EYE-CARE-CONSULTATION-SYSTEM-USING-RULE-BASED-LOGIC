import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '../context/auth-context'

export function AdminRoute() {
  const { user, loading } = useAuth()

  if (loading) return <main className="mx-auto max-w-6xl px-6 py-20" role="status">Restoring your session…</main>
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'admin') return <Navigate to="/dashboard" replace />
  return <Outlet />
}
