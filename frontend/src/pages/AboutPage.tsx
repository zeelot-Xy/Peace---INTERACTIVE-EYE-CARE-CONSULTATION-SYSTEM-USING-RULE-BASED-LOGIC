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
          The rule base remains separate from application data, cites reputable published
          guidance, and retains an explanation of why each rule matched.
        </p>
        <h2 className="pt-3 text-2xl font-bold text-slate-900 dark:text-white">How a consultation works</h2>
        <ol className="grid gap-3 pl-5 list-decimal">
          <li>Questions collect structured facts without using image recognition or machine learning.</li>
          <li>Versioned rules compare those facts and always preserve the highest safety risk.</li>
          <li>Results separate possible indications from diagnoses and explain which rules matched.</li>
          <li>Every medical statement links back to the knowledge base’s published evidence.</li>
        </ol>
        <p className="rounded-2xl bg-slate-100 p-5 text-sm dark:bg-slate-800">
          The knowledge base is transparent but has not been clinically validated. Seek qualified
          professional care whenever symptoms are severe, sudden, worsening, or concerning.
        </p>
      </div>
    </main>
  )
}
