# ADR 0006: Accessible Safety-First Patient Interface

- Status: Accepted
- Date: 2026-07-25

## Context

The consultation service exposes stateful, safety-sensitive questions and explainable results.
The patient interface must make urgent action unmistakable, preserve concurrency guarantees,
and avoid presenting possible indications as diagnoses.

## Decision

Use server-owned consultation state with one question per screen. Every mutation submits the
current revision, and conflicts reload authoritative state. Render partial urgent escalation
above the active question. Separate results into action level, red flags, recommendations,
possible indications, explanations, evidence, and limitation sections. Use semantic native
controls, responsive layouts, persistent light/dark themes, and browser print styles.

No token or answer is stored in browser storage. Report view reads the immutable result snapshot
and does not rerun inference.

## Consequences

- Patients receive safety advice as soon as the rule engine can establish an urgent pathway.
- Back navigation cannot silently overwrite another browser tab.
- Results remain explainable and reproducible.
- The browser can print a useful report, while controlled PDF generation remains a separate
  Phase 9 responsibility.
- Interface tests can assert semantic roles and wording rather than fragile visual coordinates.
