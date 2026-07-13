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
Consultation and inference engines (later phases)
        |
SQLite application data + versioned JSON knowledge
```

Routes translate HTTP requests and responses. Services own use-case coordination. The future inference engine evaluates normalized facts against a separately versioned knowledge base.

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

