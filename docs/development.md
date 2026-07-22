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
