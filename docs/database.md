# Database and Migration Guide

## Data ownership

SQLite stores dynamic application data only. Expert-system questions, symptoms, conditions, rules, recommendations, and risk levels remain outside the database and will be introduced as versioned JSON.

## Data dictionary

| Table | Purpose | Important constraints |
|---|---|---|
| `users` | Patient and administrator identities | UUID primary key; normalized unique email; hashed password; indexed role |
| `consultation_sessions` | Structural ownership shell for later consultation work | User foreign key with cascade; indexed status |
| `consultation_responses` | Future JSON answers tied to stable question IDs | Consultation foreign key; consultation/question composite index |
| `reports` | Future immutable report snapshots | One report per consultation; user ownership |
| `refresh_tokens` | Hashed refresh-token identifiers and rotation families | Unique JTI hash; expiry, use, and revocation timestamps |
| `token_revocations` | Revoked access/refresh identifiers | Unique JTI hash and expiry |
| `application_events` | Operational events without secrets | Indexed level, category, and correlation identifier |
| `audit_logs` | Security and accountability trail | Optional actor, action, resource, request metadata |

```mermaid
erDiagram
  USERS ||--o{ CONSULTATION_SESSIONS : owns
  USERS ||--o{ REFRESH_TOKENS : authenticates
  USERS ||--o{ TOKEN_REVOCATIONS : revokes
  USERS ||--o{ AUDIT_LOGS : acts
  CONSULTATION_SESSIONS ||--o{ CONSULTATION_RESPONSES : contains
  CONSULTATION_SESSIONS ||--o| REPORTS : produces
  USERS ||--o{ REPORTS : owns
```

SQLite foreign-key enforcement is enabled for every SQLAlchemy connection.

## Migration operations

From `backend/` with the virtual environment installed:

```powershell
.venv\Scripts\python -m flask --app run.py db upgrade
.venv\Scripts\python -m flask --app run.py db current
.venv\Scripts\python -m flask --app run.py db check
```

Create migrations only after model review:

```powershell
.venv\Scripts\python -m flask --app run.py db migrate -m "describe schema change"
```

Review generated upgrade and downgrade operations before applying them. Docker runs `db upgrade` before starting the API. Back up `instance/eye_care.db` while the application is stopped; restore only to the same schema revision, then run `db upgrade`.
