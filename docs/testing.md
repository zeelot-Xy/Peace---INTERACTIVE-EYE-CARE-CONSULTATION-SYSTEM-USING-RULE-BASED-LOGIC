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

## Docker verification cadence

Following the project-owner decision on 2026-07-25, routine phases use local backend and
frontend lint, test, type, and production-build gates. Full Docker image rebuilds are required
when container configuration or runtime dependencies change, and during the Phase 12 packaging
and Phase 14 final clean-machine audit. This avoids repeated CPU-intensive image work while
preserving final deployment assurance.

Phase 8 administrator verification additionally covers role denial, safe summaries and audit
serialization, bounded invalid archives, valid package diffs, explicit publication, restart
restoration, historical consultation package resolution, rollback, and audit actions. Docker
configuration and dependencies did not change, so the approved deferred-build policy applies.

Phase 9 report verification covers completed-state enforcement, owner privacy, administrator
review, idempotent generation, retained byte checksums, PDF extraction, Unicode names, missing
optional profile fields, long pagination, audit events, and server-side history filters.
Representative pages are rendered to images and visually inspected. ReportLab is a new runtime
dependency, so the deferred-build policy requires one Docker image build and live report smoke
test at the end of this phase.

## Phase 10 comprehensive verification

- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-phase10.ps1` runs the
  local whitespace, Ruff, backend coverage, ESLint, Vitest,
  TypeScript, and production-build gates in one reproducible command.
- Backend application coverage must remain at or above 90%.
- Cross-layer defence tests cover registration, CSRF, one-question consultation, emergency
  escalation, deterministic results, immutable PDF generation, filtered history, ownership,
  administration, audit safety, and stable negative API envelopes.
- React tests cover the critical patient and administrator views, accessible navigation and
  controls, stale-revision reload, retry recovery, and report failure recovery.
- `requirements-to-test-report.md` names evidence for every traceability-matrix requirement;
  an automated test prevents silent omissions.
- The live defence rehearsal follows `defence-demo.md` with fictional data only.

Phase 10 introduces no container configuration or runtime dependency change, so the approved
deferred Docker-build policy applies. The live services may be smoke-tested without rebuilding.

## Phase 11 security and privacy gates

- `scripts/verify-phase11.ps1` retains the Phase 10 lint, 90% backend coverage, frontend test,
  TypeScript, and production-build gates.
- Security-negative tests verify JSON handling, request-size rejection, rate-limit responses,
  defensive headers, explicit CORS, Unicode control rejection, audit redaction, and immutability.
- Operations tests verify SQLite backup, integrity-checked restore, dry-run retention preview,
  and explicit retention application.
- Authentication review verifies atomic refresh consumption and persisted administrator role.
- Knowledge review covers ZIP size, entries, ratio, paths, links, encryption, exact names,
  bounded reads, immutable identity, and serialized publication.
- `pip check`, `pip-audit -r requirements.txt`, and `check-npm-audit.mjs` form the dependency
  gate. The npm check accepts only the documented RSC-only advisory while that upstream fix is
  unpublished; every other high or critical production advisory fails. Network failures must
  be retried and are not treated as a clean audit.
- Docker rebuilding remains deferred because no runtime dependency or container configuration
  changed. Phases 12 and 14 retain clean-container and clean-machine checks.

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

## Phase 6 quality gates

- Service and API tests cover authenticated creation, ownership, one-question ordering,
  autosave, resume, answer revision, back navigation, progress, and history.
- Validation tests cover strict fact types, invalid question IDs, required-question skips,
  optional skips, and conditional question visibility.
- State tests cover stale revision conflicts, incomplete completion, immutable terminal states,
  cancellation, and completed result retrieval.
- Safety tests prove partial emergency escalation and that conditional logic cannot hide or
  skip safety-critical questions.
- Migration checks verify new lifecycle columns, response uniqueness, downgrade, re-upgrade,
  and schema drift.
- Earlier inference, authentication, frontend, build, Docker, hygiene, and hosted secret gates
  remain mandatory.

## Phase 7 quality gates

- Semantic frontend tests cover safety language, protected navigation, registration, login,
  profile, logout, one-question input, autosave, urgent partial guidance, result separation,
  source links, and loading/error landmarks.
- Keyboard and responsive inspection covers navigation, radio and numeric inputs, progress,
  answer review, confirmation controls, history filtering, theme switching, and print layout.
- Contract tests verify saved answers carry their original safe question context.
- TypeScript, Vite, ESLint, Ruff, all backend regressions, Docker, hygiene, and hosted secret
  checks remain mandatory.

## Phase 12 packaging gates

- `scripts/verify-phase12.ps1` inherits the complete Phase 11 regression gate and validates the
  server Compose projection with fresh non-committed secrets.
- Runtime tests cover application-data paths, first-run secrets, knowledge seeding, compiled
  frontend routing, port selection, single-instance locking, migrations, backup, restore, demo
  reset, and safe diagnostics.
- `-IncludeHeavyBuilds` creates and smokes the PyInstaller Windows archive and isolated Docker
  server deployment. It verifies first run, restart, retained accounts, stable secrets, health,
  database migrations, and volume persistence.
- Heavy builds are run at release acceptance rather than during every implementation cycle.

## Phase 13 documentation gates

- `scripts/validate_documentation.py` verifies required reader documents, every repository-local
  Markdown link, academic chapter headings, documentation-index coverage, and all 16 source IDs.
- `test_quality_evidence.py` prevents a traceability requirement from lacking named test evidence
  and checks the Phase 13 final-documentation artifacts.
- `scripts/verify-phase13.ps1` runs the Phase 12 regression gate, Compose validation, and the
  documentation validator. `-IncludeHeavyBuilds` remains available for final clean-artifact
  rehearsal.
- Passing software tests demonstrates conformance to authored requirements and tested scenarios;
  it does not establish clinical safety, diagnostic accuracy, or medical-device approval.
