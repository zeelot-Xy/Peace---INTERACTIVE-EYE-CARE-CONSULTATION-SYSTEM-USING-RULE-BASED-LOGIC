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

Evidence belongs in the phase report and evidence register. A check is not considered passed without a reproducible command or artifact.

