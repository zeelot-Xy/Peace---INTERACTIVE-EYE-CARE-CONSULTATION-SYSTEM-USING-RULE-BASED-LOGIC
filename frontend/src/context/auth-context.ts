import { createContext, useContext } from 'react'

import type { User } from '../types/auth'

export interface Credentials {
  email: string
  password: string
}

export interface Registration extends Credentials {
  full_name: string
}

export interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (credentials: Credentials) => Promise<void>
  register: (data: Registration) => Promise<void>
  logout: (all?: boolean) => Promise<void>
  refreshProfile: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used within AuthProvider')
  return value
}
