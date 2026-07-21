import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { FormField } from '../components/FormField'
import { useAuth } from '../context/auth-context'
import { apiErrorMessage } from '../lib/api'

const schema = z.object({
  email: z.email('Enter a valid email address.'),
  password: z.string().min(1, 'Enter your password.'),
})
type LoginForm = z.infer<typeof schema>

export function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [serverError, setServerError] = useState('')
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({ resolver: zodResolver(schema) })

  if (user) return <Navigate to="/dashboard" replace />

  const submit = handleSubmit(async (values) => {
    setServerError('')
    try {
      await login(values)
      const from = (location.state as { from?: string } | null)?.from
      navigate(from || '/dashboard', { replace: true })
    } catch (error) {
      setServerError(apiErrorMessage(error))
    }
  })

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Welcome back</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Sign in</h1>
      <p className="mt-3 text-slate-600">Continue to your secure eye-care consultation account.</p>
      <form className="mt-8 grid gap-5" onSubmit={submit} noValidate>
        {serverError && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-800" role="alert">{serverError}</div>}
        <FormField id="email" label="Email" type="email" autoComplete="email" error={errors.email?.message} {...register('email')} />
        <FormField id="password" label="Password" type="password" autoComplete="current-password" error={errors.password?.message} {...register('password')} />
        <button className="rounded-xl bg-teal-700 px-5 py-3 font-semibold text-white hover:bg-teal-800 disabled:opacity-60" disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p className="mt-6 text-sm text-slate-600">New here? <Link className="font-semibold text-teal-700" to="/register">Create an account</Link></p>
    </main>
  )
}
