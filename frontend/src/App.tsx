import { Activity, ArrowRight, ShieldCheck } from 'lucide-react'
import { Link, Route, Routes } from 'react-router-dom'

import { AboutPage } from './pages/AboutPage'
import { HomePage } from './pages/HomePage'

function Header() {
  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link className="flex items-center gap-2 font-semibold text-slate-900" to="/">
          <span className="grid size-9 place-items-center rounded-xl bg-teal-600 text-white">
            <Activity aria-hidden="true" size={20} />
          </span>
          EyeCare Guide
        </Link>
        <nav aria-label="Primary navigation" className="flex items-center gap-6 text-sm">
          <Link className="text-slate-600 hover:text-teal-700" to="/about">About</Link>
          <span className="rounded-full bg-slate-100 px-3 py-1.5 text-slate-500">Phase 1</span>
        </nav>
      </div>
    </header>
  )
}

function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <span className="flex items-center gap-2">
            <ShieldCheck aria-hidden="true" size={17} /> Educational support, not a diagnosis
          </span>
          <Link className="inline-flex items-center gap-1 text-teal-700" to="/about">
            Safety information <ArrowRight aria-hidden="true" size={15} />
          </Link>
        </div>
      </footer>
    </div>
  )
}

export default App

