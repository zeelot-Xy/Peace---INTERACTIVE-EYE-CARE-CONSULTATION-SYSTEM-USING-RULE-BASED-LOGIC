# Testing Strategy

## Phase 1 quality gates

- Ruff checks backend style, imports, correctness, and modernization rules.
- pytest verifies the application factory, health contract, correlation IDs, and error envelope.
- ESLint checks frontend TypeScript and React hooks.
- Vitest and Testing Library verify routing and visible safety language.
- TypeScript and Vite must produce a successful production build.
- Docker Compose configuration must resolve successfully; live container health is checked where the environment permits Docker engine access.

## Later layers

Later phases add database integration, authentication, knowledge validation, table-driven inference, consultation flows, security-negative testing, PDF verification, accessibility checks, and end-to-end defense scenarios.

## Phase 2 quality gates

- Backend integration tests create and destroy an isolated in-memory SQLite schema.
- Authentication tests cover registration, generic login failure, CSRF, refresh rotation and replay, profile updates, password revocation, audit safety, and patient/admin separation.
- Migration verification performs downgrade to base, upgrade to head, and schema-drift checking.
- Frontend tests cover public safety content, protected redirects, registration validation, and successful login navigation.
- Docker smoke testing applies migrations automatically, exercises registration/profile/logout, and verifies frontend and API health.

Evidence belongs in the phase report and evidence register. A check is not considered passed without a reproducible command or artifact.
