# Windows Release Guide

## Purpose

The Windows release is the client-friendly, single-computer edition. It contains the compiled
React interface, Flask application, Waitress server, Python runtime, database migrations, and
knowledge resources. Python, Node.js, npm, and Docker are not required on the client computer.

This edition remains an educational prototype and must not be represented as a diagnostic
medical device.

## Start and stop

1. Extract `EyeCareConsultation-Windows.zip` into a normal user-controlled folder.
2. Double-click `EyeCareConsultation.exe`.
3. The application selects port `8765`, or the next safe available loopback port, and opens the
   default browser after its health endpoint responds.
4. Close the application console window, or press `Ctrl+C`, to stop it.

The service binds only to `127.0.0.1`; another computer cannot connect to this local edition.
Only one instance can use a Windows account's application data at a time.

Before using administrator features, close the application and double-click
`Create Administrator.cmd`. Enter a new email, full name, and a password of at least 12
characters. The command refuses to promote or replace an existing patient account and never
ships a default administrator password.

## Writable data

Changing data is stored under:

```text
%LOCALAPPDATA%\EyeCareConsultation\
```

The directory contains:

- `data\eye-care.sqlite3` — accounts, consultations, reports, tokens, and audits;
- `knowledge\packages` and `knowledge\active.json` — writable retained knowledge versions;
- `config\installation-secrets.json` — random installation-specific signing secrets;
- `logs\eye-care.log` — rotating operational logs;
- `backups` — verified SQLite backups.

The executable and bundled resources remain read-only. Bundled knowledge is copied only when
the corresponding writable package does not already exist, so upgrades do not overwrite an
administrator-published version.

Do not email, upload, or commit the application-data directory. It may contain personal data
and authentication material.

## Backup, restore, reset, and diagnostics

Double-click `Backup Data.cmd` to create a transactionally consistent, integrity-checked backup.
Copy important backup files to an access-controlled external location.

Restore is deliberately command-line only:

```powershell
.\EyeCareConsultation.exe restore "D:\Backups\eye-care-20260727T120000Z.sqlite3" --confirm
```

Stop the application before restoring. The selected backup must pass SQLite integrity checks.

`Reset Demo Data.cmd` requires the operator to type `RESET`. It creates a safety backup before
removing the local database. On the next launch, migrations create a clean database. Knowledge
versions and installation secrets are preserved.

`Diagnostics.cmd` prints paths and existence/integrity states but never prints signing secrets,
tokens, passwords, or consultation content.

## Build and verification

From a configured development checkout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-windows-release.ps1
```

The command builds React once, packages a one-folder executable with PyInstaller, creates the
ZIP archive, and writes `release\SHA256SUMS.txt`. Compare the distributed archive's SHA-256
digest with that manifest before delivery.

Antivirus products can scrutinize unsigned PyInstaller applications. Code signing is outside
the academic prototype but is recommended before commercial distribution.

## Troubleshooting

- If the browser does not open, run `Diagnostics.cmd`, then inspect `logs\eye-care.log`.
- If port `8765` is occupied, the launcher automatically tries the next ports.
- If a second instance reports that the application is already running, close the existing
  console before retrying.
- If the secret file is damaged, do not delete it casually: existing login cookies would become
  invalid. Preserve the data directory and restore a known backup.
- If the database fails integrity checks, stop the application and restore a verified backup.
