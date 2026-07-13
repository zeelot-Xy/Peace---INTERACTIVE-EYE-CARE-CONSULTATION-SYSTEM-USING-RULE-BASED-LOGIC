export function AboutPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-20">
      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700">About</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight">A careful educational tool</h1>
      <div className="mt-8 space-y-5 text-base leading-7 text-slate-600">
        <p>
          The Interactive Eye Care Consultation System is a final-year project exploring how a
          transparent expert system can conduct a structured consultation and provide safe guidance.
        </p>
        <p>
          It will not diagnose conditions, prescribe treatment, or replace an optometrist,
          ophthalmologist, emergency service, or other qualified healthcare professional.
        </p>
        <p>
          The future rule base will remain separate from application data, cite reputable published
          guidance, and retain an explanation of why each rule matched.
        </p>
      </div>
    </main>
  )
}

