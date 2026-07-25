import { ArrowRight, BookOpen, BrainCircuit, ClipboardCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

const features = [
  {
    icon: ClipboardCheck,
    title: 'Conversational consultation',
    description: 'Answer one clear question at a time, leave safely, and resume from any device session.',
  },
  {
    icon: BrainCircuit,
    title: 'Transparent rule logic',
    description: 'Every recommendation is explainable and driven by versioned knowledge.',
  },
  {
    icon: BookOpen,
    title: 'Sourced guidance',
    description: 'Published eye-health sources accompany the educational knowledge base.',
  },
]

export function HomePage() {
  return (
    <main>
      <section className="mx-auto grid max-w-6xl gap-12 px-6 py-20 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">
            Interactive eye-care support
          </p>
          <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-950 sm:text-6xl">
            Clear guidance through transparent rule-based reasoning.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            This academic system helps people understand eye-related symptoms and
            appropriate next steps without presenting its output as a medical diagnosis.
          </p>
          <div className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-950">
            If you have sudden vision loss, severe eye pain, chemical exposure, or a serious eye
            injury, seek urgent professional care. Do not wait for an online consultation.
          </div>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link className="inline-flex items-center gap-2 rounded-xl bg-teal-700 px-5 py-3 font-bold text-white hover:bg-teal-800" to="/register">Start securely <ArrowRight aria-hidden="true" size={18} /></Link>
            <Link className="rounded-xl border border-slate-300 px-5 py-3 font-bold dark:border-slate-600" to="/about">How it works</Link>
          </div>
        </div>
        <div className="grid gap-4" aria-label="System qualities">
          {features.map(({ icon: Icon, title, description }) => (
            <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900" key={title}>
              <Icon aria-hidden="true" className="mb-4 text-teal-600 dark:text-teal-300" size={26} />
              <h2 className="font-semibold text-slate-900 dark:text-white">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{description}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}
