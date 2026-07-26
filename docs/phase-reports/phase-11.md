# Phase 11 Completion Report

- Phase: Security and Privacy Hardening
- Date: 2026-07-27
- Status: Ready for review

## Delivered

- Thread-safe application and endpoint rate limits with HTTP 429 and `Retry-After`
- Strict CORS, hosted secure cookies, request-size limits, JSON media checks, normalized text,
  safe error responses, and defensive browser headers
- Atomic refresh rotation and persisted-role enforcement for administrator claims
- Central log and audit redaction plus append-only application-layer audit protection
- Hardened ZIP entry, expansion, compression, path, encryption, streaming, and identity checks
- Serialized knowledge publication for the supported single-process runtime
- Verified SQLite backup and restore commands
- Dry-run-first retention maintenance and controlled patient-data deletion
- OWASP-oriented review, dependency audits, security-negative tests, and documentation

## Verification evidence

- Ruff and all 129 backend tests passed with 92.56% statement coverage.
- Python runtime dependency audit reported no known vulnerabilities.
- Frontend lint, all 17 Vitest tests, TypeScript, and the production build passed.
- npm identified high-severity advisory `GHSA-qwww-vcr4-c8h2` in React Router `7.18.1`.
  Repository and advisory evidence show it affects only unstable React Server Components APIs,
  which this Vite SPA does not use. The announced `8.3.0` fix was not published to npm at review
  time. The gate accepts only this exact temporary exception and fails every other high or
  critical production advisory.
- The pre-hardening review identified rate limiting, request sizing, refresh rotation, and
  stale-role enforcement as reportable baseline gaps. Phase 11 implements direct controls and
  regression coverage for all four.

## Architecture boundary

The in-memory rate limiter and publication lock are correct for the packaged single-process
release. A hosted multi-process deployment must use shared rate-limit state and distributed or
database publication locking. Windows database ACL and clean-machine packaging verification
remain Phase 12 responsibilities.

## Docker decision

Phase 11 adds no runtime dependency, Dockerfile, Compose, or base-image change. Under the project
owner's approved CPU-saving cadence, rebuilding is deferred to packaging and final clean-build
verification. The development-only `pip-audit` dependency does not enter the backend image.

## Safety and privacy boundary

Only fictional data was used. These controls do not clinically validate the knowledge base,
turn the prototype into a medical device, or establish compliance with a specific health-data
law. Operators remain responsible for host security, encrypted backups, scheduling, access
review, and incident response.

## Approval gate

Phase 11 requires the final clean local gate, replacement immutable security scan, pull-request
review, and explicit approval before Phase 12 begins.
