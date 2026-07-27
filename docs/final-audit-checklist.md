# Final Audit and Delivery Checklist

## Repository

- [x] All fourteen phase reports exist and accepted phases are merged through Phase 13.
- [x] Every traceability requirement has an implementation, verification, and documentation
  mapping.
- [x] No implementation TODO, FIXME, disabled gate, committed secret, database, log, backup,
  build directory, virtual environment, or `node_modules` is tracked.
- [x] Git whitespace, Ruff, ESLint, TypeScript, production build, and documentation checks pass.
- [x] GitGuardian reports no secret finding on the release pull request.

## Functional and safety

- [x] Registration, login, refresh rotation, logout, profile, and role boundaries are tested.
- [x] Consultation start, autosave, resume, revision, completion, cancellation, and ownership are
  tested.
- [x] Every knowledge rule executes through JSON without Python rule logic.
- [x] Unknown facts, conflicts, red flags, highest-risk resolution, and deterministic traces are
  tested.
- [x] Urgent advice remains prominent and possible indications remain non-diagnostic.
- [x] Immutable PDF generation, history filtering, ownership, Unicode, long content, and repeat
  download are tested.
- [x] Knowledge validation, preview, publish, retention, rollback, and audit events are tested.

## Security, privacy, and accessibility

- [x] Password hashing, cookie flags, CSRF, CORS, request limits, rate limits, safe errors,
  revocation, privilege freshness, and upload bounds have negative tests.
- [x] Audit events are redacted and protected from normal mutation.
- [x] Backup, restore, retention preview/application, deletion, and diagnostics avoid secret
  disclosure.
- [x] Keyboard semantics, accessible names, focus behavior, error recovery, responsive layout,
  light/dark presentation, and print layout have automated or recorded manual evidence.
- [x] Residual risks and the absence of clinical validation are stated consistently.

## Release artifacts

- [x] Windows build contains the compiled UI, Waitress, Python runtime, migrations, schemas, and
  knowledge without requiring development tools.
- [x] Windows first run, restart, persistent data, stable installation secrets, report
  generation, and maintenance commands are smoke-tested.
- [x] Docker server runs non-root, applies migrations, reports health, restarts, and retains data
  in its named volume.
- [x] Source ZIP, complete Git bundle, Windows ZIP, readable history, and checksum manifest are
  assembled by one command.
- [x] Demonstration identities are fictional and no default credential is distributed.

## Documentation and defence

- [x] User, administrator, development, API, database, security, testing, knowledge-authoring,
  Windows, server, troubleshooting, and client-handoff guides are linked from the index.
- [x] Academic report contains introduction, literature review, methodology/design,
  implementation/testing/results, conclusion, references, and appendices.
- [x] All medical source IDs are represented in the report and source register.
- [x] Architecture, authentication, consultation, publication, and deployment diagrams are
  available for defence.
- [x] Presentation outline and repeatable patient/administrator demonstration are available.

## Final approval actions

The following occur only after Phase 14 review approval:

1. merge the Phase 14 pull request;
2. create the immutable `v1.0.0` Git tag at the approved merge commit;
3. rebuild the handoff from that exact tag if its commit differs from the reviewed artifact;
4. verify all final SHA-256 values;
5. transfer the archive through the agreed private channel; and
6. record client receipt without recording credentials or patient data.

