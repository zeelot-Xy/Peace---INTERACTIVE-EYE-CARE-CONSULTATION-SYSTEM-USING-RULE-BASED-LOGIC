# Docker and Linux Server Deployment

## Deployment artifact

The server release uses the repository `Dockerfile` and `compose.server.yml`, not the Windows
executable. A multi-stage build compiles React with the same-origin `/api/v1` base, then copies
the assets into the Flask image. Waitress serves the API and interface from one origin.

SQLite and knowledge publication remain single-instance operations. Do not scale the container
above one application instance without first replacing SQLite, the in-memory rate limiter, and
the process-local publication lock with shared services.

## Initial server deployment

1. Install Docker Engine and the Compose plugin on a Linux server.
2. Clone or securely copy the repository.
3. Copy `.env.server.example` to `.env.server`.
4. Generate two independent random secrets of at least 32 characters and store them only in
   `.env.server`.
5. For local HTTP evaluation, retain `JWT_COOKIE_SECURE=false` and the localhost origin.
6. For an internet deployment, configure HTTPS first, set `PUBLIC_ORIGIN` to the exact public
   HTTPS origin, and set `JWT_COOKIE_SECURE=true`.
7. Start the single service:

```bash
docker compose --env-file .env.server -f compose.server.yml up -d --build
docker compose --env-file .env.server -f compose.server.yml ps
```

The default host address is `http://localhost:8080`. The internal service listens on port 5000.
Database migrations run before Waitress accepts traffic.

Create the first administrator interactively:

```bash
docker compose --env-file .env.server -f compose.server.yml exec eye-care \
  python -m flask --app run.py bootstrap-admin
```

## Persistent data

The named volume `eye-care-server-data` is mounted at `/data`. It contains SQLite, the active
knowledge pointer, retained uploaded packages, and operator-created backups. Recreating the
container does not remove the named volume. Running `docker compose down -v` deletes it and must
never be used on a system containing required data.

Create a database backup:

```bash
docker compose --env-file .env.server -f compose.server.yml exec eye-care \
  python -m flask --app run.py database-backup \
  --output /data/backups/manual-20260727.sqlite3
```

Copy the backup off the server or into a separately protected backup system. A Docker volume is
not itself a backup.

Before restoring, stop normal traffic and follow the verified restore procedure in
`security-and-privacy.md`.

## HTTPS and public exposure

Place a maintained reverse proxy or cloud load balancer in front of the container. It must:

- obtain and renew a trusted TLS certificate;
- redirect HTTP to HTTPS;
- forward the original host and protocol;
- restrict administrative network access where practical;
- impose request and connection limits;
- preserve access logs without recording cookies or tokens.

Never expose Flask's development server. Do not commit `.env.server`, secrets, database files,
or backups.

## Free-tier servers

A free VM can support an academic demonstration if it provides a persistent disk and permits a
long-running Docker service. Google Cloud documents an eligible free-tier `e2-micro` VM with
persistent disk allowance, while Oracle Cloud documents Always Free compute resources:

- <https://cloud.google.com/products/compute>
- <https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm>

Provider eligibility, regions, quotas, identity verification, and pricing can change. Confirm
the provider's current terms before deployment.

Render's free web service is not suitable for this SQLite configuration because its local
filesystem is ephemeral and free persistent disks are unavailable:

- <https://render.com/docs/free>

Free hosting is appropriate for supervised demonstrations, not sensitive or clinically relied
upon patient use. It may sleep, throttle, disappear, lack backups, or change terms.

## Updates and rollback

1. Create and verify an off-server database backup.
2. Pull the reviewed release revision.
3. Run the Phase 12 verification command.
4. Rebuild and restart the service.
5. Verify `/api/v1/health`, login, consultation history, and report download.
6. If verification fails, restore the prior image/revision and the matching verified backup.
