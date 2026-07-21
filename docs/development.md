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
```

## Configuration profiles

`APP_ENV` accepts `development`, `testing`, `production`, or `packaged`. An unknown profile fails during application creation rather than silently using unsafe defaults.

Secrets never belong in committed files. The checked-in environment example contains names and non-sensitive development defaults only.
