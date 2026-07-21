import { useCallback, useEffect, useMemo, useState } from 'react'

import { api } from '../lib/api'
import type { ApiEnvelope, User } from '../types/auth'
import { AuthContext, type Credentials, type Registration } from './auth-context'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshProfile = useCallback(async () => {
    const response = await api.get<ApiEnvelope<{ user: User }>>('/users/me')
    setUser(response.data.data?.user ?? null)
  }, [])

  useEffect(() => {
    api
      .get<ApiEnvelope<{ user: User }>>('/users/me')
      .then((response) => setUser(response.data.data?.user ?? null))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (credentials: Credentials) => {
    const response = await api.post<ApiEnvelope<{ user: User }>>('/auth/login', credentials)
    setUser(response.data.data?.user ?? null)
  }, [])

  const register = useCallback(async (data: Registration) => {
    const response = await api.post<ApiEnvelope<{ user: User }>>('/auth/register', data)
    setUser(response.data.data?.user ?? null)
  }, [])

  const logout = useCallback(async (all = false) => {
    await api.post(all ? '/auth/logout-all' : '/auth/logout')
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshProfile }),
    [user, loading, login, register, logout, refreshProfile],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
