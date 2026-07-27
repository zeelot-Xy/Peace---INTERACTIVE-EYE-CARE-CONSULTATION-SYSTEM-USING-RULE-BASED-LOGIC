# Development Guide

## Prerequisites

- Python 3.12 or newer
- Node.js 22 or newer
- npm
- Docker Desktop and Docker Compose when using containers

Copy `.env.example` to `.env` before local or Docker development and replace development secrets outside the Phase 1 demonstration environment.

## Commands

Backend and frontend commands are listed in the root README. Windows systems that block PowerShell npm scripts can use `npm.cmd` directly.

Validate the authored knowledge package separately from the Flask runtime:

```powershell
cd backend
.venv\Scripts\python tools\validate_knowledge_package.py --json
.venv\Scripts\python -m flask --app run.py knowledge-status --json
.venv\Scripts\python -m flask --app run.py knowledge-validate --json
```

## Configuration profiles

`APP_ENV` accepts `development`, `testing`, `production`, or `packaged`. An unknown profile fails during application creation rather than silently using unsafe defaults.

`KNOWLEDGE_PACKAGES_DIR`, `KNOWLEDGE_SCHEMAS_DIR`, and `KNOWLEDGE_ACTIVE_PACKAGE` select the startup snapshot. Flask fails closed if it cannot validate that package. See the runtime knowledge loading guide for recovery operations.

Secrets never belong in committed files. The checked-in environment example contains names and non-sensitive development defaults only.

## Repository layout

- `backend/app` contains routes, services, persistence, inference, runtime, and maintenance code.
- `backend/knowledge` contains schemas and immutable published packages.
- `backend/migrations` contains reviewed Alembic revisions.
- `frontend/src` contains the React application and semantic flow tests.
- `docs` contains versioned technical and academic truth.
- `packaging/windows` and `scripts` contain release and verification automation.

Routes validate and authorize, then call services. Domain or medical rules must not be added to
routes or React components. Eye-care content is changed through a new complete knowledge package
and its validation/publishing workflow.

## Typical workflow

1. Create a focused branch from current `main`.
2. Update code, tests, traceability, evidence, and the relevant guide together.
3. Run narrow tests while developing.
4. Run `scripts/verify-phase13.ps1` before review.
5. Commit with a descriptive conventional prefix such as `feat:`, `fix:`, `docs:`, or `test:`.
6. Use fictional data in tests, screenshots, Drive evidence, and Slack progress.

Do not edit generated release archives, a published knowledge package, or an existing migration
to simulate a new version. Create the governed successor artifact.

## Database and administrator setup

From `backend`, apply `python -m flask --app run.py db upgrade`. Create an administrator with
`python -m flask --app run.py bootstrap-admin`; the command is interactive, rejects unsafe
defaults, and will not silently promote a patient. See [Database](database.md) before migration,
backup, restore, or retention work.

## Final verification

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-phase13.ps1
```

Pass `-IncludeHeavyBuilds` only when a clean Windows package and Docker server smoke test are
required. These builds are reserved for release gates because they are CPU intensive. The
normal command still runs all code, dependency, build, Compose-configuration, and documentation
checks.

For focused documentation validation:

```powershell
backend\.venv\Scripts\python scripts\validate_documentation.py
```

See [Testing](testing.md), [API Reference](api-reference.md), and
[Troubleshooting](troubleshooting.md).
