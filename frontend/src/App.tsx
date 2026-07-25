import { Activity, ArrowRight, History, LayoutDashboard, LogOut, Menu, Moon, ShieldCheck, Sun, UserRound, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/auth-context'
import { AboutPage } from './pages/AboutPage'
import { ConsultationPage } from './pages/ConsultationPage'
import { DashboardPage } from './pages/DashboardPage'
import { HistoryPage } from './pages/HistoryPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { ProfilePage } from './pages/ProfilePage'
import { RegisterPage } from './pages/RegisterPage'
import { ResultsPage } from './pages/ResultsPage'

function Header() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const persistTheme = import.meta.env.MODE !== 'test'
  const [dark, setDark] = useState(() => persistTheme && window.localStorage?.getItem('eye-care-theme') === 'dark')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    if (persistTheme) window.localStorage?.setItem('eye-care-theme', dark ? 'dark' : 'light')
  }, [dark, persistTheme])

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-3 sm:px-6">
        <Link className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white" onClick={() => setOpen(false)} to="/">
          <span className="grid size-9 place-items-center rounded-xl bg-teal-600 text-white">
            <Activity aria-hidden="true" size={20} />
          </span>
          EyeCare Guide
        </Link>
        <div className="flex items-center gap-2">
          <button aria-label={`Use ${dark ? 'light' : 'dark'} mode`} className="grid size-10 place-items-center rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => setDark((value) => !value)} type="button">
            {dark ? <Sun aria-hidden="true" size={19} /> : <Moon aria-hidden="true" size={19} />}
          </button>
          <button aria-expanded={open} aria-label="Toggle navigation" className="grid size-10 place-items-center rounded-xl md:hidden" onClick={() => setOpen((value) => !value)} type="button">
            {open ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
          </button>
        </div>
        <nav aria-label="Primary navigation" className={`${open ? 'flex' : 'hidden'} absolute inset-x-0 top-full flex-col gap-2 border-b border-slate-200 bg-white p-5 text-sm shadow-lg md:static md:flex md:flex-row md:items-center md:border-0 md:bg-transparent md:p-0 md:shadow-none dark:border-slate-800 dark:bg-slate-950 md:dark:bg-transparent`}>
          <Link className="nav-link" onClick={() => setOpen(false)} to="/about">About</Link>
          {user ? (
            <>
              <Link className="nav-link" onClick={() => setOpen(false)} to="/dashboard"><LayoutDashboard aria-hidden="true" size={16} /> Dashboard</Link>
              <Link className="nav-link" onClick={() => setOpen(false)} to="/history"><History aria-hidden="true" size={16} /> History</Link>
              <Link className="nav-link" onClick={() => setOpen(false)} to="/profile"><UserRound aria-hidden="true" size={16} /> Profile</Link>
              <button className="nav-link text-red-700 dark:text-red-300" onClick={() => logout()} type="button"><LogOut aria-hidden="true" size={16} /> Sign out</button>
            </>
          ) : (
            <Link className="rounded-xl bg-teal-700 px-4 py-2 font-semibold text-white" onClick={() => setOpen(false)} to="/login">Sign in</Link>
          )}
        </nav>
      </div>
    </header>
  )
}

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/consultations/:consultationId" element={<ConsultationPage />} />
            <Route path="/consultations/:consultationId/results" element={<ResultsPage />} />
            <Route path="/reports/:consultationId" element={<ResultsPage />} />
          </Route>
        </Routes>
        <footer className="no-print border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
          <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
            <span className="flex items-center gap-2"><ShieldCheck aria-hidden="true" size={17} /> Educational support, not a diagnosis</span>
            <Link className="inline-flex items-center gap-1 text-teal-700" to="/about">Safety information <ArrowRight aria-hidden="true" size={15} /></Link>
          </div>
        </footer>
      </div>
    </AuthProvider>
  )
}

export default App
