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
Runtime knowledge loader + deterministic inference engine
        |
Consultation lifecycle and version-frozen result snapshots
        |
SQLite application data + immutable versioned JSON packages
```

Routes translate HTTP requests and responses. Services own use-case coordination. The
inference engine evaluates normalized facts against the separately versioned snapshot supplied
by the runtime loader.

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

Phase 5 registers a stateless engine at `app.extensions["inference"]`. Strictly typed facts use
three-valued logic so missing values remain unknown. Highest risk wins, recommendations come
only from that tier, and every rule retains a deterministic trace. See ADR 0004 and the
inference engine guide.

All medical assertions carry source IDs. Rules contain explanation text and cite their
evidence. Emergency rules occupy the highest priority band and require multiple sources.
Neither routes nor database models contain medical decision logic.

## Consultation boundary

Phase 6 adds an authenticated consultation service and resource layer. Each session freezes
package ID, version, and fingerprint, autosaves typed answers, and uses a monotonic revision to
detect concurrent changes. Declarative question conditions determine applicability, but
safety-critical questions always remain active. Completed results are immutable snapshots;
routes contain transport handling only.

## Patient-interface boundary

Phase 7 adds a responsive React journey over the consultation resources. The browser renders
server-owned state and submits the current revision with every mutation; it does not implement
question branching or medical rules. Partial urgent alerts precede the active question.
Completed snapshots are rendered as separate action, red-flag, recommendation, possible-
indication, explanation, evidence, and disclaimer sections. HttpOnly authentication remains
unchanged, and browser storage contains only the non-sensitive theme preference.

## Administration boundary

Phase 8 adds administrator-only reporting and knowledge governance. Uploaded archives are
bounded, inspected, staged, passed through the shared validator, and compared with the active
snapshot. A candidate is retained under a unique package ID but remains inactive until an
explicit publish request revalidates and atomically activates it. The active ID and fingerprint
are persisted outside the package directory and verified during startup. Retired versions are
never overwritten, allowing frozen consultations and controlled rollback to resolve the exact
package they reference. See ADR 0007 and the administration guide.

## Report boundary

Phase 9 composes an immutable PDF from the completed result, stored answers, frozen package,
and a generation-time patient snapshot. The service stores both the composition JSON and exact
PDF bytes with a checksum; later downloads never rerun inference or read the current profile.
Owner-scoped resources and governed administrator access protect retrieval. See ADR 0008 and
the reports and history guide.

## Verification boundary

Phase 10 links every implemented requirement to named automated and review evidence. A
cross-layer Flask scenario exercises the patient safety path through immutable report
generation, while React interaction tests verify browser semantics and recovery behavior. The
canonical verification command enforces a 90% backend application-coverage floor alongside
lint, component tests, type checking, and production build. Test passage establishes software
conformance for authored scenarios; it does not establish clinical validity.
