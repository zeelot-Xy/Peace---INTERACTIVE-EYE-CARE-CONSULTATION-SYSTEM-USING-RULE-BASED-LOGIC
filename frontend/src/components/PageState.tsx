import { AlertCircle, LoaderCircle, RefreshCw } from 'lucide-react'

export function PageLoading({ message = 'Loading your information…' }: { message?: string }) {
  return (
    <main className="mx-auto flex max-w-6xl items-center gap-3 px-6 py-20 text-slate-600 dark:text-slate-300" role="status">
      <LoaderCircle aria-hidden="true" className="animate-spin text-teal-700" />
      {message}
    </main>
  )
}

export function PageError({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <main className="mx-auto max-w-3xl px-6 py-20">
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-950 dark:border-red-900 dark:bg-red-950 dark:text-red-100" role="alert">
        <AlertCircle aria-hidden="true" />
        <h1 className="mt-4 text-2xl font-bold">We could not load this page</h1>
        <p className="mt-2">{message}</p>
        {retry && (
          <button className="mt-5 inline-flex items-center gap-2 rounded-xl bg-red-800 px-4 py-2 font-semibold text-white" onClick={retry} type="button">
            <RefreshCw aria-hidden="true" size={17} /> Try again
          </button>
        )}
      </div>
    </main>
  )
}
