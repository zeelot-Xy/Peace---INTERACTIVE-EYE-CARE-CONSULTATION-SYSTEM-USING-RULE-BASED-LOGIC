import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../context/auth-context'

export function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <main className="mx-auto max-w-6xl px-6 py-20" role="status">Restoring your session…</main>
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <Outlet />
}
