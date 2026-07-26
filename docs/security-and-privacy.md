# Security and Privacy Guide

Phase 11 applies defence in depth to the academic prototype. These controls reduce common web,
authentication, upload, logging, and local-data risks; they do not make the application a
clinically validated system or replace an independently managed production security programme.

## Request and browser boundary

- Credentialed CORS accepts explicit HTTP or HTTPS origins only. Wildcards, credentials, paths,
  queries, and fragments are rejected during startup.
- Hosted production always uses `Secure` JWT cookies. The packaged localhost profile is the
  documented exception because it is served only on the local machine.
- Cookie JWTs retain double-submit CSRF protection, `HttpOnly`, narrow paths, and
  `SameSite=Lax`.
- Flask rejects requests larger than `REQUEST_MAX_BYTES` before JSON or multipart parsing.
- JSON resources require `application/json`.
- Names and phone values are normalized with Unicode NFKC and reject invisible control or
  formatting characters. Passwords are deliberately not normalized.
- API responses set `nosniff`, frame denial, no-referrer, restrictive permissions and content
  security policies, and `no-store`. HTTPS responses also set HSTS.
- Unexpected failures return the generic API envelope and correlation identifier.

## Rate limiting

The thread-safe application-local limiter protects every API endpoint. Login, registration,
refresh, and knowledge upload have stricter configurable limits. Exceeded limits return HTTP 429
with `Retry-After`.

The implementation matches the packaged single-process release. A future multi-instance hosted
deployment must use a shared limiter such as Redis or an API-gateway control so counters remain
consistent across processes.

## Authentication and privilege controls

Refresh rotation uses an atomic conditional database update. Only one request can change an
unused, unrevoked, unexpired refresh record; a replay revokes the token family. Access-token
validation also rejects an administrator claim when the persisted account no longer has the
administrator role. Existing inactive-user, logout, logout-all, password-change, CSRF, and
generic-login-error controls remain active.

## Knowledge upload controls

Only administrators can upload packages, and CSRF remains required. The ZIP reader:

- caps compressed request bytes, expanded bytes, entry count, and compression ratio;
- rejects absolute paths, parent traversal, links, encrypted entries, unsupported compression,
  duplicate or unexpected names, and incomplete packages;
- reads each entry through a bounded stream and checks actual bytes against declared size;
- writes only the eight normalized expected filenames to a UUID staging directory;
- runs the complete schema, checksum, reference, and safety validator before retention.

Publication revalidates the retained directory and compares package ID, schema version, content
version, and fingerprint to the immutable database record. An in-process lock serializes publish
and rollback for the supported single-process runtime.

## Logging and audit protection

Audit payloads pass through a bounded recursive sanitizer. Keys associated with passwords,
tokens, secrets, authorization, cookies, CSRF, and sessions become `[REDACTED]`. Application and
Werkzeug loggers also redact common header and credential patterns. Audit model events reject
application-layer updates and deletes; ordinary routes expose no audit mutation resource.

Audit records must never contain consultation answers, passwords, JWTs, CSRF values, raw
cookies, or private document content.

## Data retention and deletion

| Data | Default retention |
|---|---:|
| In-progress or cancelled consultations | 90 days after last update |
| Completed consultations and reports | 365 days after completion |
| Expired refresh and revocation metadata | 30 additional days |
| Audit evidence | Retained; no automatic purge |

Preview eligible records without changing data:

```powershell
cd backend
.venv\Scripts\python -m flask --app run.py privacy-maintenance
```

Apply the purge:

```powershell
.venv\Scripts\python -m flask --app run.py privacy-maintenance --apply
```

Delete one patient and cascade their consultations, responses, reports, and tokens:

```powershell
.venv\Scripts\python -m flask --app run.py delete-user-data USER_UUID --confirm
```

Administrator deletion is refused because it requires a separate governance review. Minimal
audit evidence may retain an opaque UUID but not the deleted profile or consultation data.

## Backup and restore

Create a transactionally consistent, integrity-checked backup:

```powershell
.venv\Scripts\python -m flask --app run.py database-backup
```

Restore requires an explicit acknowledgement and verifies both source and result:

```powershell
.venv\Scripts\python -m flask --app run.py database-restore PATH_TO_BACKUP --confirm
```

Stop normal traffic before restore. Keep backups in access-controlled or encrypted storage;
never copy real patient data into Drive, Slack, tests, or screenshots.

## Local SQLite permissions

Development data belongs in the Flask instance directory. Phase 12 will place packaged writable
data under the current user's `%LOCALAPPDATA%`. Operating-system account permissions are the
security boundary: never place the database in a shared or web-served directory. Windows ACL
packaging checks remain mandatory in Phase 12.

## Dependency and OWASP review

Phase verification runs `pip check`, `pip-audit` against runtime Python requirements, and checks
the audited npm production tree. React Router `7.18.1` resolves the older router advisories. Its
remaining `GHSA-qwww-vcr4-c8h2` advisory affects only unstable React Server Components APIs,
which this Vite single-page application does not use. The announced fixed `8.3.0` package was
not published to npm at review time. `check-npm-audit.mjs` accepts only this exact temporary
exception and fails on every other high or critical production advisory; remove the exception
when a compatible fixed package is published.

The review covers authentication, authorization, injection, upload, error handling, security
configuration, logging, and data protection. Residual limitations include the single-process
limiter, unvalidated clinical knowledge, local SQLite deployment, and operator responsibility
for host security, encrypted backups, and maintenance scheduling.
