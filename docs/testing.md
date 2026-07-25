# Testing Strategy

## Phase 1 quality gates

- Ruff checks backend style, imports, correctness, and modernization rules.
- pytest verifies the application factory, health contract, correlation IDs, and error envelope.
- ESLint checks frontend TypeScript and React hooks.
- Vitest and Testing Library verify routing and visible safety language.
- TypeScript and Vite must produce a successful production build.
- Docker Compose configuration must resolve successfully; live container health is checked where the environment permits Docker engine access.

## Later layers

Later phases add table-driven inference, consultation flows, security-negative testing, PDF verification, accessibility checks, and end-to-end defence scenarios.

## Phase 2 quality gates

- Backend integration tests create and destroy an isolated in-memory SQLite schema.
- Authentication tests cover registration, generic login failure, CSRF, refresh rotation and replay, profile updates, password revocation, audit safety, and patient/admin separation.
- Migration verification performs downgrade to base, upgrade to head, and schema-drift checking.
- Frontend tests cover public safety content, protected redirects, registration validation, and successful login navigation.
- Docker smoke testing applies migrations automatically, exercises registration/profile/logout, and verifies frontend and API health.

Evidence belongs in the phase report and evidence register. A check is not considered passed without a reproducible command or artifact.

## Phase 3 quality gates

- Draft 2020-12 meta-validation checks every schema.
- The authoring validator verifies package structure, semantic version consistency, SHA-256 values, stable IDs, cross-references, citations, prohibited wording, emergency evidence, and risk order.
- Positive tests validate the accepted package and its minimum approved scope.
- Negative tests alter content to prove checksum tampering, broken references, diagnostic wording, and invalid risk order are detected.
- The full backend, frontend, build, Docker, and secret-scanning gates remain mandatory even when application runtime behavior is unchanged.

## Phase 4 quality gates

- Loader tests cover valid and invalid JSON, schemas, inventory, versions, checksums, IDs, references, and deterministic reports.
- Snapshot tests cover deep immutability, read-only indexes, cache identity, change invalidation, and forced reload.
- Activation tests prove invalid candidates preserve the last valid package and missing initial knowledge prevents startup.
- Concurrency tests prove simultaneous readers observe one complete fingerprint.
- Factory and CLI tests verify extension registration, status output, candidate-only validation, JSON contracts, and exit codes.
- Backend/frontend lint, tests, build, Docker startup, live status, placeholder, and secret checks remain phase acceptance gates.

## Phase 5 quality gates

- Expression tests cover all comparisons, nested logic, effective negation, and strong-Kleene
  truth tables.
- Fact tests cover unknown IDs, omitted versus null values, exact types, ranges, choices, and
  immutability.
- Engine tests cover ordering, highest-risk conflicts, recommendation suppression, no-match
  and incomplete outcomes, deduplication, score wording, stable traces, and concurrency.
- Scenario tests make all current rules match and prove a new JSON rule executes without
  Python changes.
- CLI tests verify machine-readable output and non-zero invalid-input behavior.
- All earlier lint, test, build, Docker, placeholder, and secret gates remain mandatory.
