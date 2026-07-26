# Administration and Knowledge Governance

## Access boundary

Only authenticated users whose JWT role is `admin` may use `/api/v1/admin` or the React
administrator workspace. Patient requests receive `403 forbidden`. Administrator creation
remains an interactive CLI operation; the application contains no default administrator
password.

The workspace reports account and consultation totals, recent safe account records,
consultation result snapshots, audit events, and retained knowledge versions. It never exposes
password hashes, tokens, or consultation answers in audit events.

## Knowledge-package workflow

1. Author and peer-review a complete package using the knowledge-authoring guide.
2. Produce a ZIP containing exactly `manifest.json` and the seven required JSON collections.
   A single enclosing folder is accepted.
3. Upload the ZIP in **Admin → Knowledge versions**.
4. Inspect structural and safety validation, collection-level changes, warnings, and affected
   rule IDs.
5. Publish only when the report is valid and the displayed changes match the intended review.

The server limits compressed and extracted size, rejects traversal paths and symbolic links,
requires the exact package inventory, and never overwrites an existing package ID or
fingerprint. Invalid input cannot replace active knowledge.

## Publication and rollback

Publishing revalidates the retained directory, atomically activates the immutable snapshot,
writes a fingerprint-protected active-state file, retires the previous database record, and
records an audit event. A restart reads this state file and refuses to start if the retained
directory no longer matches its published fingerprint.

Rollback uses the same validation and activation path. It does not copy or modify package
content. Every prior directory remains available so consultations can resolve their frozen
package ID and fingerprint. Publication affects only consultations created afterwards.

## API resources

| Method | Resource | Purpose |
|---|---|---|
| `GET` | `/api/v1/admin/summary` | Account, consultation, and report counts |
| `GET` | `/api/v1/admin/users` | Paginated safe account listing |
| `GET` | `/api/v1/admin/consultations` | Paginated consultation overview |
| `GET` | `/api/v1/admin/consultations/{id}/report` | Stored result snapshot and provenance |
| `GET` | `/api/v1/admin/audit-logs` | Paginated audit events |
| `GET` | `/api/v1/admin/knowledge` | Retained versions and validation/diff metadata |
| `GET` | `/api/v1/admin/knowledge/{id}` | One version record |
| `POST` | `/api/v1/admin/knowledge/validate` | Upload and validate multipart field `package` |
| `POST` | `/api/v1/admin/knowledge/{id}/publish` | Publish a valid candidate |
| `POST` | `/api/v1/admin/knowledge/{id}/rollback` | Reactivate a retained prior version |

All responses use the standard envelope. State-changing calls require the access-token CSRF
header.

## Operational recovery

- Validation fails: correct the authored archive; the active snapshot remains unchanged.
- Publication revalidation fails: restore the retained directory from the source archive and
  investigate the audit event. No activation occurs.
- Startup reports state mismatch: do not edit the state file to bypass the check. Restore the
  matching immutable package or a verified backup of both the package store and state file.
- Incorrect valid version published: use **Roll back to version** after confirming the target
  fingerprint.

The knowledge base is a sourced but not clinically validated academic prototype. Administrator
publication is governance control, not clinical certification.
