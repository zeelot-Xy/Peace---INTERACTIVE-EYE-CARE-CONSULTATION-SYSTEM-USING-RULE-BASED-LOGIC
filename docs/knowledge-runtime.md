# Runtime Knowledge Loading and Recovery

## Purpose and boundary

Phase 4 makes a validated JSON package available to Flask as an immutable runtime snapshot. It does not execute rules, choose a risk level, branch a consultation, or publish uploaded packages. Those responsibilities remain in later approval-gated phases.

The application refuses to start unless its configured package passes every structural, integrity, reference, evidence, and safety check. This fail-closed behavior prevents the API from operating with partial medical guidance.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `KNOWLEDGE_PACKAGES_DIR` | `backend/knowledge/packages` | Parent directory of immutable packages |
| `KNOWLEDGE_SCHEMAS_DIR` | `backend/knowledge/schemas` | Draft 2020-12 schema directory |
| `KNOWLEDGE_ACTIVE_PACKAGE` | `eye-care-en-1.0.0` | Package directory selected at startup |
| `KNOWLEDGE_RELOAD_ON_CHANGE` | `false` | Reserved development reload policy; no request-time polling occurs |
| `KNOWLEDGE_STATE_FILE` | application instance `knowledge-active.json` | Atomic active package ID and fingerprint written by Phase 8 publication |
| `KNOWLEDGE_UPLOAD_MAX_BYTES` | `5242880` | Maximum uploaded and expanded candidate size |

Paths may be absolute. Relative paths are resolved from the process working directory, which is `backend/` in the documented local and Docker commands.

## Load and activation sequence

1. Resolve the candidate and schema directories to canonical paths.
2. Read and validate the manifest before trusting its file inventory.
3. Reject unsupported schema versions.
4. Validate all seven documents against their schemas.
5. Verify canonical SHA-256 checksums, content versions, IDs, references, citations, risk order, emergency evidence, and prohibited wording.
6. Compute a deterministic package fingerprint.
7. Recursively freeze JSON objects into read-only mappings and tuples, then build ID indexes.
8. Atomically exchange the active reference only after all prior steps succeed.

JSON checksum input normalizes CRLF to LF. This preserves the authored checksums across Windows, Linux, and Docker while still detecting content changes.

## Cache and concurrency

`KnowledgeManager` caches by canonical package path and a metadata signature covering the manifest, declared files, and schema files. Repeated unchanged loads return the same immutable object. A metadata change triggers complete revalidation and a new fingerprint. A forced load bypasses the cache.

A re-entrant process lock protects cache writes and activation. Readers receive either the complete old snapshot or the complete new snapshot; they cannot observe an intermediate package. The cache is process-local and performs no filesystem writes.

## Validation report contract

Every validation produces deterministic JSON-compatible fields:

```json
{
  "valid": true,
  "package_id": "eye-care-en-1.0.0",
  "schema_version": "1.0.0",
  "content_version": "1.0.0",
  "fingerprint": "sha256 fingerprint",
  "issues": []
}
```

Each issue has a stable `code`, `location`, and safe `message`. Reports contain no timestamp, so equal input produces equal output and tests can compare reports exactly.

## Operations

From `backend/`:

```powershell
.venv\Scripts\python tools\validate_knowledge_package.py --json
.venv\Scripts\python -m flask --app run.py knowledge-validate --json
.venv\Scripts\python -m flask --app run.py knowledge-status --json
```

Pass a candidate path to `knowledge-validate` to inspect it without changing the active package. A valid command exits `0`; an invalid candidate exits `1`.

## Failure and recovery

- Startup failure: correct the configured path or package, run the validator, then restart Flask.
- Candidate activation failure: the manager returns the issue report and keeps the last valid snapshot active.
- Changed active directory fails reload: restore the immutable directory from version control or select a separately validated package directory. Do not repair an active directory in place in production.
- Missing prior snapshot: startup or `get_active()` fails clearly; there is no empty or partially valid fallback.

Authenticated administration provides upload, preview, publication, retention, and rollback. Before the
first administrator publication, package selection uses `KNOWLEDGE_ACTIVE_PACKAGE`. Afterwards,
startup reads `KNOWLEDGE_STATE_FILE` and fails closed if the named directory or fingerprint no
longer matches. See the administration guide for the complete workflow.
