import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { FormField } from '../components/FormField'
import { useAuth } from '../context/auth-context'
import { apiErrorMessage } from '../lib/api'

const schema = z
  .object({
    full_name: z.string().trim().min(2, 'Enter your full name.').max(120),
    email: z.email('Enter a valid email address.'),
    password: z.string().min(12, 'Use at least 12 characters.').max(128),
    confirm_password: z.string(),
  })
  .refine((values) => values.password === values.confirm_password, {
    message: 'Passwords do not match.',
    path: ['confirm_password'],
  })
type RegistrationForm = z.infer<typeof schema>

export function RegisterPage() {
  const { register: createAccount, user } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegistrationForm>({ resolver: zodResolver(schema) })

  if (user) return <Navigate to="/dashboard" replace />

  const submit = handleSubmit(async (formValues) => {
    setServerError('')
    try {
      const values = {
        full_name: formValues.full_name,
        email: formValues.email,
        password: formValues.password,
      }
      await createAccount(values)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setServerError(apiErrorMessage(error))
    }
  })

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Patient account</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Create your account</h1>
      <p className="mt-3 text-slate-600">Only minimal identity information is required.</p>
      <form className="mt-8 grid gap-5" onSubmit={submit} noValidate>
        {serverError && <div className="rounded-xl bg-red-50 p-4 text-sm text-red-800" role="alert">{serverError}</div>}
        <FormField id="full-name" label="Full name" autoComplete="name" error={errors.full_name?.message} {...register('full_name')} />
        <FormField id="register-email" label="Email" type="email" autoComplete="email" error={errors.email?.message} {...register('email')} />
        <FormField id="register-password" label="Password" type="password" autoComplete="new-password" error={errors.password?.message} {...register('password')} />
        <FormField id="confirm-password" label="Confirm password" type="password" autoComplete="new-password" error={errors.confirm_password?.message} {...register('confirm_password')} />
        <button className="rounded-xl bg-teal-700 px-5 py-3 font-semibold text-white hover:bg-teal-800 disabled:opacity-60" disabled={isSubmitting} type="submit">
          {isSubmitting ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="mt-6 text-sm text-slate-600">Already registered? <Link className="font-semibold text-teal-700" to="/login">Sign in</Link></p>
    </main>
  )
}
