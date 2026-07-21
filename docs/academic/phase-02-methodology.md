# Phase 2 Academic Methodology Notes

Phase 2 applied a layered, security-conscious implementation method. Database entities represent application-generated records, while the planned expert knowledge remains a separate JSON concern. Alembic migrations provide a reproducible schema history, and SQLite foreign keys protect ownership relationships.

Authentication uses short-lived access credentials, rotating refresh credentials, CSRF protection, password hashing, server-side revocation records, and role-based authorization. This design reduces exposure compared with storing bearer tokens in browser storage and provides an auditable explanation of session invalidation.

Verification combines unit and integration tests for validation, persistence, authentication, authorization, token replay, and auditing with frontend tests for forms, redirects, session establishment, and safety language. Migration downgrade/upgrade testing confirms repeatability before deployment testing.

The phase does not introduce medical knowledge, consultation reasoning, diagnosis, or clinical claims. This preserves the project's staged methodology and keeps security evidence separate from later expert-system evaluation.
