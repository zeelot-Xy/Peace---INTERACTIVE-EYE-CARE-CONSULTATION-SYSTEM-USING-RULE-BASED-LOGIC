# Phase 7 Academic Methodology: Patient Interaction Design

Phase 7 applied a safety-centred, task-oriented interaction design to the rule-based
consultation lifecycle. The design decomposed the patient journey into orientation,
authentication, structured fact collection, immediate red-flag communication, result
interpretation, and historical review.

The consultation uses progressive disclosure by presenting one question at a time. This reduces
visual load while the server remains responsible for ordering, branching, progress, and
knowledge-version reproducibility. Optimistic concurrency is surfaced as recovery rather than a
technical error: stale updates reload the authoritative session before the patient continues.

Risk communication follows a hierarchy. Urgent action is rendered before the active question
and uses explicit language, an alert landmark, iconography, and colour. Possible indications
occupy a separate section labelled as symptom patterns rather than diagnoses. Recommendations,
rule explanations, evidence links, match-score limitations, and the mandatory disclaimer are
presented as distinct information groups.

Evaluation combines automated semantic interaction tests, TypeScript and production-build
checks, backend regression tests, responsive browser inspection, keyboard navigation, dark-mode
inspection, error-state inspection, and a live container patient flow. This evaluates functional
correctness and usability while acknowledging that formal clinical validation and usability
studies with representative patients remain future work.
