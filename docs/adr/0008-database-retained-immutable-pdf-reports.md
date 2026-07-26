# ADR 0008: Retain Immutable PDF Reports in SQLite

- Status: Accepted
- Date: 2026-07-26

## Context

Completed reports must remain reproducible after patient profile edits, knowledge publication,
application restart, or repeated download. Storing only a path or regenerating on demand could
lose the original content, depend on mutable files, or create different output for the same
consultation.

## Decision

Generate a report once from the completed result, frozen knowledge package, stored responses,
and a patient snapshot. Store both the JSON composition snapshot and exact PDF bytes in the
`reports` row, with a SHA-256 checksum, MIME type, and safe filename. Enforce one report per
consultation. Repeat creation returns the retained artifact.

Patient access is owner-scoped; administrators receive governed read access. Report creation
and download are audited. The browser receives no database path and uses an authenticated,
no-store download resource.

## Consequences

This design gives byte-for-byte repeatability, simple single-machine backup, and no orphaned
report files. SQLite size grows with report volume, which is acceptable for the packaged
academic prototype but not an unlimited hosted deployment. Phase 11 must define retention and
deletion, and future multi-user scaling may move encrypted report blobs to controlled object
storage while retaining the same immutable metadata contract.
