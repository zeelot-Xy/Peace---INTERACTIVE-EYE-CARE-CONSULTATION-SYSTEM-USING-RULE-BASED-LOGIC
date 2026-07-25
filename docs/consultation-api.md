# Consultation Lifecycle and API

## Boundary

Phase 6 coordinates authenticated consultations over the immutable knowledge and inference
subsystems. It does not add patient-facing consultation screens, PDF reports, knowledge
publishing, or new medical claims.

All resources are under `/api/v1/consultations`, use HttpOnly-cookie authentication and CSRF
protection, and retain the standard `{data, errors, correlation_id}` envelope.

## Resources

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/consultations` | Start a consultation and freeze active knowledge identity |
| `GET` | `/consultations` | List the authenticated patient's history |
| `GET` | `/consultations/{id}` | Resume or inspect one owned consultation |
| `PUT` | `/consultations/{id}/responses/{question_id}` | Autosave, revise, or explicitly skip |
| `DELETE` | `/consultations/{id}/responses/{question_id}` | Clear a response for back navigation |
| `POST` | `/consultations/{id}/complete` | Validate completeness and freeze the result |
| `POST` | `/consultations/{id}/cancel` | Cancel an in-progress consultation |
| `GET` | `/consultations/{id}/result` | Read a completed immutable result snapshot |

Create returns HTTP 201. Ownership failures use the same 404 response as unknown IDs.

## One-question state

Every consultation representation contains:

- status and integer revision;
- frozen package ID, content version, and SHA-256 fingerprint;
- resolved, applicable, and percentage progress;
- the next applicable unanswered question;
- saved answers and explicitly skipped optional questions;
- an urgent safety alert when partial inference reaches urgent or emergency risk; and
- lifecycle timestamps.

Question order follows the frozen package. Optional `show_when` expressions use the same
tri-state expression language as rules. A branch appears only when its condition is true.
Safety-critical questions are always applicable, even if an authored condition is present, so
branching cannot bypass red-flag collection.

## Autosave, revision, and skip contract

Answer writes use:

```json
{
  "answer": true,
  "skip": false,
  "revision": 3
}
```

The exact symptom type, integer bounds, and choice set are validated from frozen knowledge.
Every successful mutation increments `revision`. A stale revision receives HTTP 409 with
`consultation_revision_conflict`; the client must reload before retrying. This prevents two
browser tabs from silently overwriting each other.

Set `skip` to true only for optional, non-safety questions. A skip cannot include an answer.
Revising an upstream answer removes responses and skips that are no longer applicable.

## Completion and reproducibility

Completion fails while any applicable question remains unresolved. This includes every
safety-critical question regardless of branching. The engine evaluates the saved facts against
the session's frozen package. The complete inference result, trace, sources, disclaimer,
package version, and fingerprint are stored as an immutable JSON snapshot.

Active sessions use the exact package fingerprint captured at creation. If the active package
later changes, the loader resolves the original package directory and verifies its fingerprint
before allowing the session to continue. A missing or mismatched historical package fails
closed.

Completed and cancelled consultations cannot be changed. Phase 9 will compose downloadable
reports from completed snapshots without rerunning current knowledge.

## Privacy and audit

Audit records capture lifecycle action, consultation ID, revision, question ID, skip state,
knowledge fingerprint, and final risk ID. They never contain answer values or tokens.
Consultations and results are accessible only to their owning patient in Phase 6.
