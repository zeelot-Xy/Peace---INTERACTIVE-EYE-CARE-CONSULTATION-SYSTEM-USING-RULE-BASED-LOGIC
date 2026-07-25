import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { FormField } from '../components/FormField'
import { useAuth } from '../context/auth-context'
import { api, apiErrorMessage } from '../lib/api'

const profileSchema = z.object({
  full_name: z.string().trim().min(2).max(120),
  phone: z.string().max(30),
  date_of_birth: z.string(),
})
const credentialSchema = z.object({
  current_password: z.string().min(1, 'Enter your current password.'),
  new_password: z.string().min(12, 'Use at least 12 characters.').max(128),
})
type ProfileForm = z.infer<typeof profileSchema>
type CredentialForm = z.infer<typeof credentialSchema>

export function ProfilePage() {
  const { user, refreshProfile, logout } = useAuth()
  const navigate = useNavigate()
  const [notice, setNotice] = useState('')
  const [serverError, setServerError] = useState('')
  const profile = useForm<ProfileForm>({ resolver: zodResolver(profileSchema) })
  const credentialForm = useForm<CredentialForm>({ resolver: zodResolver(credentialSchema) })

  useEffect(() => {
    if (user) profile.reset({ full_name: user.full_name, phone: user.phone ?? '', date_of_birth: user.date_of_birth ?? '' })
  }, [user, profile])

  const saveProfile = profile.handleSubmit(async (values) => {
    setServerError('')
    try {
      await api.patch('/users/me', { ...values, phone: values.phone || null, date_of_birth: values.date_of_birth || null })
      await refreshProfile()
      setNotice('Profile updated successfully.')
    } catch (error) {
      setServerError(apiErrorMessage(error))
    }
  })

  const submitCredentialChange = credentialForm.handleSubmit(async (values) => {
    setServerError('')
    try {
      await api.post('/users/me/password', values)
      navigate('/login', { replace: true })
    } catch (error) {
      setServerError(apiErrorMessage(error))
    }
  })

  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">Account</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">Profile and security</h1>
      {notice && <div className="mt-6 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800" role="status">{notice}</div>}
      {serverError && <div className="mt-6 rounded-xl bg-red-50 p-4 text-sm text-red-800" role="alert">{serverError}</div>}
      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-xl font-semibold">Personal details</h2>
          <p className="mt-2 text-sm text-slate-600">Your email is fixed for this phase: {user?.email}</p>
          <form className="mt-6 grid gap-5" onSubmit={saveProfile}>
            <FormField id="profile-name" label="Full name" error={profile.formState.errors.full_name?.message} {...profile.register('full_name')} />
            <FormField id="phone" label="Phone (optional)" type="tel" autoComplete="tel" error={profile.formState.errors.phone?.message} {...profile.register('phone')} />
            <FormField id="date-of-birth" label="Date of birth (optional)" type="date" error={profile.formState.errors.date_of_birth?.message} {...profile.register('date_of_birth')} />
            <button className="rounded-xl bg-teal-700 px-5 py-3 font-semibold text-white disabled:opacity-60" disabled={profile.formState.isSubmitting}>Save profile</button>
          </form>
        </section>
        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-xl font-semibold">Password</h2>
          <form className="mt-6 grid gap-5" onSubmit={submitCredentialChange}>
            <FormField id="current-password" label="Current password" type="password" autoComplete="current-password" error={credentialForm.formState.errors.current_password?.message} {...credentialForm.register('current_password')} />
            <FormField id="new-password" label="New password" type="password" autoComplete="new-password" error={credentialForm.formState.errors.new_password?.message} {...credentialForm.register('new_password')} />
            <button className="rounded-xl border border-slate-300 px-5 py-3 font-semibold text-slate-800 disabled:opacity-60" disabled={credentialForm.formState.isSubmitting}>Change password</button>
          </form>
          <div className="mt-8 border-t border-slate-200 pt-6">
            <button className="text-sm font-semibold text-red-700" onClick={() => logout(true)} type="button">Sign out from every device</button>
          </div>
        </section>
      </div>
    </main>
  )
}
