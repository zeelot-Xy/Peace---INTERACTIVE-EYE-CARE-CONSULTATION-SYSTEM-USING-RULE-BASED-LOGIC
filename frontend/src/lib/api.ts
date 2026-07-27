import axios from 'axios'

function readCookie(name: string): string | undefined {
  return document.cookie
    .split('; ')
    .find((entry) => entry.startsWith(`${name}=`))
    ?.split('=')[1]
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 10_000,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const method = config.method?.toLowerCase()
  if (method && !['get', 'head', 'options'].includes(method)) {
    const csrfCookie = config.url?.includes('/auth/refresh')
      ? 'csrf_refresh_token'
      : 'csrf_access_token'
    const token = readCookie(csrfCookie)
    if (token) config.headers.set('X-CSRF-TOKEN', decodeURIComponent(token))
  }
  return config
})

let refreshRequest: Promise<void> | null = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config as typeof error.config & { _retried?: boolean }
    const excluded = ['/auth/login', '/auth/register', '/auth/refresh']
    const canRetry =
      error.response?.status === 401 &&
      request &&
      !request._retried &&
      !excluded.some((path) => request.url?.includes(path))

    if (!canRetry) return Promise.reject(error)
    request._retried = true
    refreshRequest ??= api.post('/auth/refresh').then(() => undefined)
    try {
      await refreshRequest
      return api(request)
    } finally {
      refreshRequest = null
    }
  },
)

export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.errors?.[0]?.message ?? 'The request could not be completed.'
  }
  return 'The request could not be completed.'
}

