# ADR 0007: Retained Atomic Knowledge Publication

- Status: Accepted
- Date: 2026-07-26

## Context

Administrators need to preview and publish authored knowledge without invalidating consultations
that froze an earlier package. Directly replacing an active directory would make historical
results irreproducible and could expose readers to a partially copied update.

## Decision

Each valid package ID and fingerprint is retained in its own immutable directory and recorded in
SQLite. Uploads are extracted into a private staging directory, validated, diffed against the
active snapshot, and moved into retention only after success. Publication revalidates the
retained directory, activates it through the locked knowledge manager, then atomically replaces
a small state file containing the package ID and fingerprint.

Prior versions are retired, not deleted. Rollback invokes the same activation mechanism.
Consultations continue resolving their stored package ID and fingerprint.

## Consequences

- Invalid or interrupted uploads cannot alter the active snapshot.
- A published selection survives restart and detects filesystem tampering.
- Historical consultations remain reproducible.
- Package IDs cannot be reused for changed content; authors must increment semantic versions.
- Multi-instance hosted publication would require shared storage and coordinated activation,
  which remains outside the single-machine version-one scope.
