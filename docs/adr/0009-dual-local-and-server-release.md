# ADR 0009: Dual Local and Server Release

- Status: Accepted
- Date: 2026-07-27

## Context

The client needs an edition that runs without development tools and may later want access from
multiple computers through a hosted address. A Windows executable and a Linux server have
different writable-path, network, secret, and lifecycle requirements.

## Decision

Deliver two projections of the same Flask/React application:

1. a PyInstaller one-folder Windows release that binds to loopback and stores mutable data under
   the current user's `%LOCALAPPDATA%`; and
2. a single-instance Docker/Linux release that stores mutable data in a mounted `/data` volume
   and receives secrets and public-origin configuration from its deployment environment.

Both projections compile React into Flask-served static assets and use same-origin `/api/v1`
requests. Bundled schemas and seed knowledge are read-only; runtime packages and the active
pointer are writable. Database migrations execute before traffic is accepted.

## Consequences

- The client can operate locally without Python, Node.js, or Docker.
- The same reviewed source can be hosted without repackaging the Windows executable.
- SQLite remains appropriate only for one application process.
- Public deployment requires HTTPS, persistent storage, backups, and operator-managed secrets.
- Horizontal scaling requires a future migration to PostgreSQL and shared coordination controls.
- Free-tier hosting is a demonstration option, not an availability or data-protection guarantee.
