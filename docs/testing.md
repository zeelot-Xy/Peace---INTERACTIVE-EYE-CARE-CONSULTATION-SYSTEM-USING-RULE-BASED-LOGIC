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
