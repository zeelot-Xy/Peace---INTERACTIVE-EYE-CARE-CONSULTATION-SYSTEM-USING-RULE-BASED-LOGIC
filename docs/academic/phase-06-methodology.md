# Phase 6 Methodology: Stateful Consultation Coordination

## Method

Phase 6 applied a state-machine design around the Phase 5 inference engine. A consultation
moves from `in_progress` to exactly one terminal state: `completed` or `cancelled`. Responses
are normalized facts keyed through authored questions and persisted after each mutation.

Optimistic concurrency uses a monotonic revision supplied by the client. A write is accepted
only when the supplied revision equals stored state, preventing lost updates without
long-running database locks.

## Branching and safety

Applicable questions preserve authored order. Optional conditions use the same three-valued
logic as inference, avoiding a second rule language. Unknown or false conditions do not expose
a conditional question. Safety-critical questions override conditional visibility and cannot
be skipped. Completion independently verifies that all applicable questions are resolved.

Partial facts are evaluated after each response. Only urgent and emergency matches are surfaced
as immediate safety alerts; lower-risk partial matches remain internal until completion.

## Reproducibility

Each session stores package ID, semantic content version, and canonical fingerprint. Continued
evaluation verifies that fingerprint. Completion stores the entire inference result as a JSON
snapshot, making later history and reporting independent of a newly active package.

## Evaluation

Tests cover creation, ownership, autosave, resume, revision, back navigation, strict answers,
optional skips, conditional visibility, mandatory safety questions, incomplete completion,
full completion, result reproducibility, history, cancellation, CSRF, stale writes, and
partial emergency escalation.

## Limitation

The current knowledge package intentionally asks all 36 adult questions and contains no
conditional `show_when` fields. Branching and optional-skip behavior are runtime capabilities
for future validated packages. The API remains an educational prototype and has not undergone
clinical usability validation.
