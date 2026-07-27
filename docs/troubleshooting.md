# Troubleshooting Guide

Start with the correlation ID shown by the interface or API response. It can be matched to
redacted application logs without exposing credentials. Never share `.env` files, secret files,
cookies, database copies, reports, or real patient data in public support channels.

## Local development

### A port is already in use

This project reserves frontend port `5173` and API port `5000` for development. Stop the process
using the port or change this project's environment and update the
[port registry](port-registry.md). The Windows release selects a free loopback port
automatically and does not require these development ports.

### Backend does not start

1. Confirm the virtual environment and dependencies are installed.
2. Copy `.env.example` to `.env` and use non-production development secrets.
3. Run `python -m flask --app run.py db upgrade` from `backend`.
4. Run `python -m flask --app run.py knowledge-validate --json`.
5. Inspect the first safe error and correlation ID; do not bypass failed migrations or knowledge
   validation.

### Frontend cannot reach the API

Confirm both services are running, `VITE_API_BASE_URL` matches the API origin, and the origin is
listed in development CORS configuration. A direct browser visit to a protected endpoint
correctly returns `401` when no cookie is present.

## Authentication

- Repeated `401`: sign in again; the refresh family may be expired or revoked.
- `403` on a state-changing request: reload once so Axios can obtain the current CSRF cookie.
  Do not disable CSRF.
- Patient receives `403` from `/admin/*`: expected role enforcement.
- Password change signs out other devices: expected session revocation.
- Repeated `429`: wait for the displayed retry period; do not weaken the limiter in production.

## Database and migrations

Back up before upgrades. Use the documented CLI backup operation, verify its integrity result,
then apply migrations. Never edit the Alembic version table manually.

If a restore fails, preserve the current database, confirm the selected backup is a valid SQLite
file, and rerun the verified restore command while the application is stopped. A failed restore
must not replace the current database. See [Database](database.md) and
[Security and privacy](security-and-privacy.md).

## Knowledge package problems

Run candidate validation and read every machine-readable error. Common causes are a missing
declared file, checksum mismatch, duplicate ID, broken cross-reference, incompatible schema
version, unsupported wording, or missing citation. Publishing accepts only a complete ZIP that
passes the same validation used at startup. A failed update leaves the last valid package
active. Do not edit a retained published package in place.

## Consultation and reports

- Stale answer conflict: reload the consultation and reapply the intended response.
- Completion rejected: answer every currently applicable required question.
- Urgent banner appears early: follow the urgent advice; this is intentional partial inference.
- PDF generation rejected: only a completed owned consultation can generate a report.
- Long PDF: content flows onto additional pages; verify the checksum if transfer corruption is
  suspected.

## Windows release

Run the included diagnostics command first. It reports paths, port selection, migration state,
and safe configuration without printing secrets. Application state is under
`%LOCALAPPDATA%\EyeCareConsultation`, not beside the executable.

- Browser did not open: copy the loopback address from the log into the browser.
- Another instance message: use the already-running browser tab or close the existing process.
- Port fallback: expected when the preferred port is occupied.
- Startup migration fails: retain the data directory and restore the last verified backup.
- Reset refuses to run: use the explicit confirmation required by the demo reset command.

Do not delete the application-data directory as a first repair step; it contains accounts,
consultations, reports, knowledge state, and installation secrets.

## Docker/server release

Confirm the required secrets are set, the persistent `/data` volume is mounted and writable,
and the health endpoint succeeds. Use `docker compose logs backend` for redacted service output.
Health-probe requests appearing every few seconds are normal.

For public access, terminate HTTPS at a trusted reverse proxy, keep secure cookies enabled,
restrict the allowed origin, and retain one application process while SQLite and local locks
are used. A free host that removes the persistent volume will erase operational state on
redeployment. Follow [Server deployment](server-deployment.md).

## Escalation record

When requesting technical support, provide:

- application edition and version;
- operating system or container platform;
- time and correlation ID;
- exact safe error text;
- the operation attempted; and
- whether a verified backup exists.

Redact names, email addresses, answers, tokens, secrets, and report content.

