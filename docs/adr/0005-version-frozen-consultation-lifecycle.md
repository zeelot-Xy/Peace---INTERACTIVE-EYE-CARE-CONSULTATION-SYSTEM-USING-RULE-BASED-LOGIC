# ADR 0005: Version-Frozen Consultation Lifecycle

- Status: Accepted
- Date: 2026-07-25

## Context

Consultations span multiple requests and may be resumed after knowledge changes. Concurrent
browser tabs can also submit different answers. Conditional branching must not allow unanswered
red flags to disappear, and historical outcomes must remain defensible.

## Decision

Freeze package ID, content version, and fingerprint when a consultation starts. Resolve every
later operation against that exact snapshot. Autosave one typed response per question and use a
monotonic integer revision for optimistic concurrency.

Compute applicable questions from authored order and optional tri-state `show_when`
expressions. Safety-critical questions always remain applicable. Require every applicable
question to be answered or explicitly skipped before completion; required and safety questions
cannot be skipped.

Persist the completed inference result as an immutable snapshot. Audit metadata about actions
but never store answer values in audit events.

## Consequences

- Resume and historical results remain tied to defensible knowledge.
- Stale clients receive an explicit conflict instead of losing data.
- Conditional paths can shorten future consultations without weakening red-flag coverage.
- The current package asks all questions because its first version has no authored branches;
  the runtime supports validated branching packages without Python changes.
- Completed results use additional SQLite storage but no longer depend on current knowledge.
- Patient UI orchestration remains Phase 7 work.
