# ADR 0002: Versioned, Sourced Knowledge Contract

- Status: Accepted
- Date: 2026-07-21

## Context

The expert-system knowledge must be independently reviewable, explainable during project defence, reproducible for historical consultations, and extensible without embedding medical claims in Flask routes or Python inference code. Medical assertions also require visible provenance and conservative safety wording.

## Decision

Use immutable semantic-versioned JSON packages validated against JSON Schema Draft 2020-12. A manifest declares scope, status, content version, disclaimer, file-to-schema mapping, and SHA-256 digests. Stable IDs connect sources, facts, questions, possible indications, recommendations, risks, and rules.

The initial package supports English-speaking adults aged 18 and older. It uses four monotonically ordered risk levels. Emergency rules require priority 900 or higher and at least two source citations. Build-time validation rejects malformed structures, mixed versions, duplicate IDs, broken references, checksum changes, unsafe ordering, and selected prohibited phrases.

## Consequences

- Knowledge changes are reviewable as data diffs and do not require Python rule changes.
- A consultation can later freeze a package content version for reproducibility.
- Source provenance and explanation templates travel with each rule.
- Checksums detect accidental or unauthorized content changes.
- Runtime caching, last-valid fallback, publishing, and rollback still require Phase 4 and Phase 8 implementation.
- Automated wording checks reduce obvious risks but do not replace clinical validation or expert review.
