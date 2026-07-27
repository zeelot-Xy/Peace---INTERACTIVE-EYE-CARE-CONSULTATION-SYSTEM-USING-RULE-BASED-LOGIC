# Project Defence Presentation Outline

## Slide 1 — Title

Project title, candidate, department, supervisor, institution, and date.

## Slide 2 — Problem and motivation

- Eye symptoms range from routine concerns to time-sensitive emergencies.
- Unstructured online advice can create delay or false reassurance.
- The project provides sourced educational guidance without claiming diagnosis.

## Slide 3 — Aim, objectives, scope

State the aim and six objectives from the academic report. Emphasize adult, English-language,
patient/administrator scope and the exclusions: imaging, machine learning, prescriptions,
appointments, telemedicine, and clinical integration.

## Slide 4 — Method

Show the approval-gated fourteen-phase process, requirements traceability, published-source
acquisition, fictional test data, and the explicit absence of clinician or patient studies.

## Slide 5 — Architecture

Use the system-context and layered-component diagrams. Explain React, `/api/v1`, Flask services,
SQLite operational data, versioned JSON knowledge, inference, and immutable PDFs.

## Slide 6 — Knowledge representation

Show stable IDs, schema/content versions, checksums, source registry, questions, conditions,
rules, recommendations, and risk levels. Explain validation, retained versions, and rollback.

## Slide 7 — Rule engine

Present a compact rule example. Explain strict facts, `AND`/`OR`/`NOT`, three-valued unknown
semantics, priorities, highest-risk conflict resolution, match score versus probability, and
the inference trace.

## Slide 8 — Patient journey

Show registration, one-question consultation, autosave/resume, early urgent alert, explainable
result, history, and PDF report. State the disclaimer before discussing outcomes.

## Slide 9 — Administration and governance

Show role denial, summaries, audit logs, knowledge validation/diff preview, atomic publication,
retention, and rollback.

## Slide 10 — Security, privacy, and accessibility

Summarize cookie JWTs, refresh rotation, CSRF, ownership, rate/request limits, safe uploads,
redacted audits, backup/retention operations, semantic controls, keyboard support, responsive
layout, and dark mode.

## Slide 11 — Verification results

- 154 backend tests and 91.30% statement coverage
- 17 frontend tests
- lint, type, production-build, migration, dependency, knowledge, security-negative, and
  documentation gates
- Windows first-run/restart persistence smoke
- non-root Docker health/restart/volume smoke

Clarify that these prove software conformance for tested scenarios, not clinical accuracy.

## Slide 12 — Demonstration

Follow [Defence Demonstration](defence-demo.md): emergency chemical-exposure patient path,
immutable report, patient/admin denial, valid knowledge preview, publication, and historical
version preservation.

## Slide 13 — Contributions and limitations

Contributions: transparent data-driven rules, incomplete-fact safety, early escalation,
version-frozen results, governed knowledge, reproducible reports, and dual delivery.

Limitations: no expert review, clinical validation, user study, paediatric scope, multilingual
content, distributed scale, or medical-device assessment.

## Slide 14 — Conclusion and future work

Conclude that the implementation requirements were met. Recommend clinical expert review,
ethics-approved usability and safety evaluation, localization, managed database scaling,
multilingual support, and regulatory assessment before clinical use.

## Likely defence questions

- Why rule-based logic instead of machine learning?
- How is unknown different from false?
- How are conflicting rules resolved?
- Why is the score not a diagnostic probability?
- How can an examiner reproduce an old report?
- How does a knowledge update avoid breaking active sessions?
- Why SQLite, and when must it be replaced?
- What evidence supports the rules?
- What does the security model protect, and what remains an operator responsibility?
- What must happen before real clinical deployment?
