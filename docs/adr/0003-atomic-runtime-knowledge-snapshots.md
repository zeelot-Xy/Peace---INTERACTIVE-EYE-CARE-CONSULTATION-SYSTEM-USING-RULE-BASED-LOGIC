# ADR 0003: Atomic Runtime Knowledge Snapshots

- Status: Accepted
- Date: 2026-07-22

## Context

The Flask application needs fast access to authored medical guidance, but an incomplete or invalid update must never replace usable knowledge. Concurrent requests also need a stable view while a later administration workflow validates a candidate package.

## Decision

Load packages into deeply immutable, process-local snapshots. Validate and index a complete candidate before exchanging the active reference under a lock. Cache unchanged packages using file metadata and a deterministic content fingerprint. Preserve the last valid active object when candidate validation fails, and fail application startup when no valid initial package exists.

Validation is shared by the authoring CLI and runtime manager. Checksums normalize Git line endings to make integrity results platform-independent. Validation reports are deterministic and machine-readable, with stable issue codes and no timestamps.

## Consequences

- Readers cannot observe partial knowledge and require no defensive copying.
- Invalid changes cannot silently degrade the running system.
- Startup configuration errors are visible immediately.
- Each process maintains its own cache; hosted multi-process synchronization will require the Phase 8 publication mechanism.
- Filesystem watching and request-time reload polling are intentionally absent. Reload is explicit and testable.
- Rule evaluation remains independent and begins in Phase 5.
