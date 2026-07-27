# Changelog

All notable changes are documented here using a simplified Keep a Changelog format.

## [Unreleased]

### Added

- Phase 1 project governance, application scaffolding, verification, and documentation foundation.
- Connected Google Drive project workspace, native project tracker, private Slack coordination channel, and kickoff draft.
- Phase 2 SQLite schema, migrations, secure cookie authentication, profile APIs, minimal authenticated UI, tests, and documentation.
- Phase 3 Draft 2020-12 knowledge schemas, sourced adult eye-care package, deterministic authoring validator, safety tests, and knowledge-authoring documentation.
- Phase 4 fail-closed runtime validation, immutable indexed knowledge snapshots, safe cache invalidation, atomic last-valid activation, operational CLI commands, tests, and documentation.
- Phase 5 strict fact validation, tri-state rule evaluation, safety-first conflict resolution, explainable traces, rule-match scoring, local inference CLI, tests, and documentation.
- Phase 6 version-frozen consultation sessions, autosave and revision control, conditional question capability, safety escalation, completion snapshots, authenticated lifecycle APIs, tests, and documentation.
- Phase 7 responsive and accessible patient interface with one-question consultation, immediate urgent escalation, history, explainable results, printable report view, dark mode, tests, and documentation.
- Phase 8 administrator workspace, operational summaries, audit and result review, retained knowledge-package validation, diff preview, atomic publication, rollback, tests, and documentation.
- Phase 9 immutable PDF reports, checksum-backed reproducibility, secure report APIs, filtered patient history, patient download controls, tests, and documentation.
- Phase 10 cross-layer defence scenarios, a 90% backend coverage gate, React accessibility and recovery checks, executable requirements-to-test evidence, and a repeatable verification command.
- Phase 11 request throttling and limits, strict browser and CORS controls, atomic token rotation, privilege-state checks, upload hardening, redacted immutable audits, dependency review, and governed SQLite retention, backup, restore, and deletion operations.
- Phase 12 unified same-origin runtime, persistent Windows application-data policy, installation
  secrets, safe launcher and maintenance tools, PyInstaller release pipeline, and persistent
  Docker/Linux server deployment.
- Phase 13 complete patient and API guides, cross-environment troubleshooting, architecture
  diagrams, adaptable academic manuscript, consolidated traceability, and automated
  documentation integrity verification.
- Phase 14 final audit checklist, client handoff guide, safe demonstration procedure, defence
  presentation outline, portable source and Git history packaging, checksum manifest, and
  delivery verification automation.

### Security

- Added a narrowly scoped audit exception for React Router advisory `GHSA-qwww-vcr4-c8h2`,
  which affects unused unstable RSC APIs; every other high or critical advisory still fails.
- Closed the baseline gaps for authentication throttling, request size, refresh rotation, and
  stale administrator claims.
