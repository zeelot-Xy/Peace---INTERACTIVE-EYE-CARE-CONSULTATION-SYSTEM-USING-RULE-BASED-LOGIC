# Client Handoff Guide

## Delivery inventory

The final handoff archive contains:

- `EyeCareConsultation-Source.zip` — reviewed source at the release commit;
- `EyeCareConsultation-Git.bundle` — complete portable Git history;
- `EyeCareConsultation-Windows.zip` — self-contained Windows edition;
- `Git-History.txt` — human-readable commit record;
- `SHA256SUMS.txt` — SHA-256 values for delivery artifacts; and
- `HANDOFF-README.md` — this operating guide.

The source archive also contains the Docker/server configuration, migrations, knowledge package,
tests, academic report, user and administrator guides, source register, and presentation
outline. Generated databases, secrets, logs, backups, virtual environments, `node_modules`, and
real patient data are excluded.

## Verify delivery

In PowerShell, compare each received file with `SHA256SUMS.txt`:

```powershell
Get-FileHash -Algorithm SHA256 .\EyeCareConsultation-Windows.zip
Get-FileHash -Algorithm SHA256 .\EyeCareConsultation-Source.zip
Get-FileHash -Algorithm SHA256 .\EyeCareConsultation-Git.bundle
```

A differing hash means the file is incomplete or changed and should not be used.

Verify the Git bundle:

```powershell
git bundle verify .\EyeCareConsultation-Git.bundle
git clone .\EyeCareConsultation-Git.bundle EyeCareConsultation
```

## Choose an edition

Use the Windows edition for a single client computer without Python, Node.js, or Docker. It
binds only to that computer and stores mutable data for the current Windows user. Follow
[Windows Release](windows-release.md).

Use the Docker/Linux edition when authorized users need a shared server. It requires Docker,
persistent storage, HTTPS for public access, independently generated secrets, and managed
backups. It remains a single application instance while SQLite and process-local controls are
used. Follow [Server Deployment](server-deployment.md).

## First-run acceptance

1. Verify checksums.
2. Start the selected edition without repairing files or changing source code.
3. Confirm `/api/v1/health` succeeds.
4. Create the administrator through the documented interactive command.
5. Register a fictional patient.
6. Complete the emergency demonstration and generate its PDF.
7. Restart the application and confirm the account, history, report, and active knowledge
   remain available.
8. Create and integrity-check a backup.
9. Confirm a patient cannot access administrator resources.

Record the operating system, release commit, checksums, date, and result. Do not record
credentials or report content.

## Knowledge and clinical boundary

The installed knowledge package is sourced and transparent but has not been clinically
validated. A client must not advertise the software as a diagnosis, prescription, medical
device, emergency service, or replacement for an eye-care professional. Knowledge updates must
be complete, versioned, cited, validated, previewed, and published through the administrator
workflow.

## Backup and transfer

The Windows data directory and server `/data` volume contain sensitive operational information.
Back up through the application command, store backups in an access-controlled location, and
test restoration. Do not copy a live SQLite file while the application is writing to it.

Before transferring the system to another operator:

- stop normal access;
- create and verify a final backup;
- transfer artifacts and backups separately;
- rotate server secrets and temporary demonstration credentials; and
- document who is responsible for hosting, backups, retention, and knowledge review.

## Support evidence

Use the [Troubleshooting Guide](troubleshooting.md). A support request should contain only the
edition, release commit, operating system, time, correlation ID, safe error text, attempted
operation, and backup status.

