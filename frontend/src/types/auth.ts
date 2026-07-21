export interface User {
  id: string
  email: string
  full_name: string
  role: 'patient' | 'admin'
  is_active: boolean
  phone: string | null
  date_of_birth: string | null
  created_at: string
}

export interface ApiError {
  code: string
  field?: string
  message: string
}

export interface ApiEnvelope<T> {
  data: T | null
  errors: ApiError[]
  correlation_id: string
}
