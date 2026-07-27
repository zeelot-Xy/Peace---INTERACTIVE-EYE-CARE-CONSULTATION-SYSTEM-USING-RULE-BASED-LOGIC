# Phase 12 Academic Methodology

Phase 12 applies reproducible-release engineering to transform the verified development system
into two client-operable artifacts. The method separates immutable program resources from
mutable operational state, because installed applications and container images can be replaced
while accounts, consultations, reports, knowledge versions, and backups must survive.

The Windows projection bundles the compiled React interface, Flask code, Waitress server,
Python runtime, migrations, schemas, and seed knowledge using PyInstaller. First-run
initialization creates installation-specific random signing secrets and writable directories
under the current Windows user's local application-data area. Loopback binding, delayed browser
launch, deterministic port fallback, and single-instance locking constrain the local trust
boundary.

The server projection uses a multi-stage Docker build. Node.js exists only in the build stage;
the runtime image contains the compiled interface and Python service. Configuration is injected
at deployment, while a named volume retains the SQLite database and knowledge state. Same-origin
delivery removes the development CORS dependency. HTTPS remains an infrastructure
responsibility and is mandatory for public use.

Verification progresses from inexpensive deterministic tests to expensive artifact checks.
Unit tests cover path resolution, persistent secrets, knowledge seeding, static routing, port
selection, instance locking, database backup, restore, reset, and diagnostics. Existing
application tests guard functional behavior. The final gate builds the Windows distribution and
Docker image once, then exercises startup, health, persistence, and artifact integrity.

Successful packaging demonstrates reproducible software delivery, not clinical validation,
regulatory approval, unlimited scalability, or guaranteed availability on a free hosting tier.
