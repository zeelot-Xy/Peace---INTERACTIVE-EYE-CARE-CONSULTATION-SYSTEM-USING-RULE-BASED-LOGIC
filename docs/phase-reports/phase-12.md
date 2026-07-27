# Phase 12 Completion Report

- Phase: Packaging and Deployment
- Date: 2026-07-27
- Status: Ready for review

## Delivered

- Unified same-origin Flask/React production runtime
- Windows `%LOCALAPPDATA%` path policy and first-run installation secrets
- Writable knowledge seeding without overwriting retained versions
- Waitress loopback launcher with safe port selection and single-instance locking
- Automatic migrations and rotating local logs
- Verified backup, restore, protected demo reset, and non-sensitive diagnostics
- PyInstaller one-folder specification, release archive script, and SHA-256 manifest
- Multi-stage Docker/Linux image with non-root runtime and persistent `/data` volume
- Server Compose configuration with required secrets and explicit origin/cookie policy
- Windows, server, architecture-decision, and academic-methodology documentation

## Verification evidence

- Ruff and all 152 backend tests passed with 91.30% statement coverage.
- Frontend lint, all 17 Vitest tests, TypeScript, and the Vite production build passed.
- Python runtime dependencies reported no known vulnerabilities; the scoped React Router
  RSC-only npm exception remains unchanged and no other high or critical production advisory
  was accepted.
- The PyInstaller one-folder build completed and produced a 31,968,481-byte ZIP archive.
- Windows artifact smoke testing verified compiled frontend delivery, health, first-run
  migrations, random persistent installation secrets, patient registration, authenticated
  consultation creation, process restart, retained user/database state, and stable secrets.
- The multi-stage Docker image built successfully under the non-root account.
- An isolated Compose project verified health, database migrations, container restart, and
  retained SQLite data in the named volume; its disposable container, network, and volume were
  removed afterward.
- Release archive SHA-256:
  `ba6aee0ffc94e17d56acd3a630de759821af0a6276ce8e60daa14b88960fb1c0`.

## Boundaries

The Windows edition is single-computer and loopback-only. The Docker edition is single-process
while SQLite, application-local rate limiting, and publication locking remain in use. Public
hosting requires HTTPS and independently governed backups. Free-tier deployment is suitable
only for academic demonstration.

## Approval gate

Phase 12 requires passing local quality checks, one Windows package build and smoke test, one
Docker image build and live persistence smoke test, pull-request review, and explicit approval
before Phase 13.
