# Architecture Overview

## Purpose and safety boundary

The system provides educational eye-care consultation support through explicit rules. It does not diagnose, prescribe, or replace professional care. Safety escalation takes precedence over convenience or condition matching.

## Layered structure

```text
React user interface
        |
Versioned REST API (/api/v1)
        |
Flask routes and validation
        |
Application services
        |
Runtime knowledge loader + inference engine (Phase 5)
        |
SQLite application data + immutable versioned JSON packages
```

Routes translate HTTP requests and responses. Services own use-case coordination. The future inference engine evaluates normalized facts against the separately versioned snapshot supplied by the runtime loader.

## Phase 1 runtime profiles

- **Development:** Vite and Flask development servers with explicit CORS origins.
- **Testing:** isolated Flask application configuration and jsdom frontend tests.
- **Docker:** two development containers with a persistent application-data volume.
- **Production:** Waitress-backed Flask container and an Nginx-served frontend build.
- **Packaged:** reserved production profile for the Phase 12 Windows release.

## Current public API

`GET /api/v1/health` returns the standard response envelope:

```json
{
  "data": {
    "service": "eye-care-api",
    "status": "healthy",
    "timestamp": "ISO-8601 UTC timestamp",
    "version": "0.1.0"
  },
  "errors": [],
  "correlation_id": "request correlation identifier"
}
```

Phase 2 adds cookie-authenticated `/api/v1/auth`, `/api/v1/users`, and `/api/v1/admin` resources. See the authentication contract for the complete endpoint table.

## Persistence and authentication flow

The application factory initializes SQLAlchemy, Alembic, and JWT management. Routes validate transport data and call services; services own password, token, revocation, and audit behavior. Browser tokens remain in HttpOnly cookies, while CSRF values are returned in separate readable cookies and echoed in request headers.

## Knowledge boundary

Phase 3 establishes immutable knowledge packages. A package manifest freezes semantic version, adult English-language scope, disclaimer, file inventory, and SHA-256 digests. Draft 2020-12 schemas define sources, facts, questions, possible indications, recommendations, ordinal risk levels, and declarative rules.

Phase 4 validates the configured package during Flask creation, recursively freezes it, builds read-only ID indexes, and exposes it through `app.extensions["knowledge"]`. A metadata cache returns the same object for unchanged files. Candidate activation is atomic, invalid candidates preserve the last valid snapshot, and startup fails if no valid snapshot can be established. See ADR 0003 and the runtime loading guide.

All medical assertions carry source IDs. Rules contain explanation text and cite their evidence. Emergency rules occupy the highest priority band and require multiple sources. Phase 5 will execute the rules. Neither routes nor database models contain medical decision logic.
