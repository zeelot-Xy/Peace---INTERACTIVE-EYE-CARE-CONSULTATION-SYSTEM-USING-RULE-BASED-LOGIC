# Interactive Eye Care Consultation System

An educational consultation-support application that uses transparent rule-based logic to provide eye-care guidance. It does **not** diagnose disease or replace professional medical advice.

## Project status

Phases 1–4 established the governed React/Flask foundation, secure persistence and
authentication, sourced eye-care knowledge, and fail-closed immutable runtime loading. Phase 5
adds deterministic tri-state rule evaluation, safety-first conflict resolution, and explainable
results. Phase 6 adds authenticated, version-frozen consultation lifecycle APIs with autosave,
resume, concurrency protection, safety escalation, and reproducible results. Phase 7 adds the
responsive patient experience for consultation, history, explainable results, printable report
view, profile management, and accessible light/dark presentation. Phase 8 adds administrator
summaries, audit review, safe knowledge-package validation and diffing, atomic publication, and
retained rollback. Downloadable PDFs remain in Phase 9.

## Technology

- React 19, Vite, TypeScript, Tailwind CSS
- Flask REST API with Python
- SQLite for application data
- Versioned JSON Schema Draft 2020-12 knowledge packages
- pytest, Vitest, Testing Library, ESLint, and Ruff
- Docker Compose for reproducible development

## Local development

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
Copy-Item ..\.env.example ..\.env
.venv\Scripts\python -m flask --app run.py db upgrade
.venv\Scripts\python -m flask --app run.py run --debug
```

The API health endpoint is `http://localhost:5000/api/v1/health`.

Create the first administrator interactively after applying migrations:

```powershell
.venv\Scripts\python -m flask --app run.py bootstrap-admin
```

### Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

The frontend runs at `http://localhost:5173` and reads `VITE_API_BASE_URL` from the environment.

### Verification

```powershell
cd backend
.venv\Scripts\python -m pytest
.venv\Scripts\python -m ruff check .
.venv\Scripts\python tools\validate_knowledge_package.py --json
.venv\Scripts\python -m flask --app run.py knowledge-status --json
.venv\Scripts\python -m flask --app run.py inference-evaluate --facts-file examples\demo-facts-emergency.json --json

cd ..\frontend
npm.cmd run lint
npm.cmd run test
npm.cmd run build
```

### Docker development

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Documentation

Project governance, architecture, testing, academic-report development, evidence tracking, and phase reports are maintained in [`docs/`](docs/README.md).

## Safety statement

This project is an academic prototype. Its knowledge base uses published sources and transparent citations but has not been clinically validated. It supports adults only and never diagnoses or prescribes. Urgent symptoms must always be referred to qualified eye-care or emergency professionals.
