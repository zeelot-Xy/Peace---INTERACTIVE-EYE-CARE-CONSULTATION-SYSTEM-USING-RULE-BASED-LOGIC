# Evidence Register

| Evidence ID | Phase | Description | Repository location | Date |
|---|---:|---|---|---|
| E-P1-001 | 1 | Backend pytest and Ruff output | Phase 1 completion report | 2026-07-13 |
| E-P1-002 | 1 | Frontend test, lint, and build output | Phase 1 completion report | 2026-07-13 |
| E-P1-003 | 1 | Docker Compose configuration validation | Phase 1 completion report | 2026-07-13 |
| E-P1-004 | 1 | Initial architecture decision | `docs/adr/0001-layered-json-knowledge-architecture.md` | 2026-07-13 |
| E-P2-001 | 2 | Backend authentication and persistence checks | Phase 2 completion report | 2026-07-13 |
| E-P2-002 | 2 | Frontend authentication checks and production build | Phase 2 completion report | 2026-07-13 |
| E-P2-003 | 2 | Migration downgrade, upgrade, and drift check | Phase 2 completion report | 2026-07-13 |
| E-P2-004 | 2 | Docker authentication smoke test | Phase 2 completion report | 2026-07-13 |
| E-P2-005 | 2 | GitGuardian clean-history security check | GitHub pull request #1 | 2026-07-21 |
| E-P3-001 | 3 | Draft 2020-12 schemas and valid versioned package | `backend/knowledge/` | 2026-07-21 |
| E-P3-002 | 3 | Source provenance and evidence mapping | `docs/source-register.md` | 2026-07-21 |
| E-P3-003 | 3 | Positive and negative authoring-validation tests | Phase 3 completion report | 2026-07-21 |
| E-P3-004 | 3 | Scope, safety, and knowledge-representation decision | ADR 0002 and Phase 3 methodology | 2026-07-21 |
| E-P3-005 | 3 | Backend/frontend lint, tests, and production build | Phase 3 completion report | 2026-07-21 |
| E-P3-006 | 3 | Docker image build and live service smoke test | Phase 3 completion report | 2026-07-21 |
| E-P3-007 | 3 | GitGuardian hosted security check and user approval | GitHub pull request #2 | 2026-07-22 |
| E-P4-001 | 4 | Runtime loader, immutable contracts, and atomic manager | `backend/app/knowledge/` | 2026-07-22 |
| E-P4-002 | 4 | Positive, negative, cache, concurrency, factory, and CLI tests | Phase 4 completion report | 2026-07-22 |
| E-P4-003 | 4 | Runtime operations and recovery guide | `docs/knowledge-runtime.md` | 2026-07-22 |
| E-P4-004 | 4 | Atomic snapshot architecture decision and methodology | ADR 0003 and Phase 4 methodology | 2026-07-22 |
| E-P4-005 | 4 | Hosted GitGuardian security check | GitHub pull request #3 | 2026-07-22 |
| E-P5-001 | 5 | Deterministic inference implementation and contracts | `backend/app/inference/` | 2026-07-23 |
| E-P5-002 | 5 | Expression, fact, rule, scenario, concurrency, and CLI tests | Phase 5 completion report | 2026-07-23 |
| E-P5-003 | 5 | Inference semantics and explainability guide | `docs/inference-engine.md` | 2026-07-23 |
| E-P5-004 | 5 | Safety-first inference decision and methodology | ADR 0004 and Phase 5 methodology | 2026-07-23 |
| E-P5-005 | 5 | Approved and merged inference implementation | GitHub pull request #4 | 2026-07-25 |
| E-P6-001 | 6 | Consultation lifecycle service, routes, and persistence | `backend/app/services/consultation_service.py` | 2026-07-25 |
| E-P6-002 | 6 | Lifecycle, safety, ownership, concurrency, and API tests | Phase 6 completion report | 2026-07-25 |
| E-P6-003 | 6 | Consultation API and reproducibility guide | `docs/consultation-api.md` | 2026-07-25 |
| E-P6-004 | 6 | Version-frozen lifecycle decision and methodology | ADR 0005 and Phase 6 methodology | 2026-07-25 |
| E-P6-005 | 6 | Approved and merged consultation lifecycle | GitHub pull request #5 | 2026-07-25 |
| E-P7-001 | 7 | Patient consultation, history, results, report, profile, and navigation interface | `frontend/src/` | 2026-07-25 |
| E-P7-002 | 7 | Semantic patient-flow and safety tests | Phase 7 completion report | 2026-07-25 |
| E-P7-003 | 7 | Patient journey, accessibility, privacy, and recovery guide | `docs/patient-interface.md` | 2026-07-25 |
| E-P7-004 | 7 | Safety-first interface decision and interaction methodology | ADR 0006 and Phase 7 methodology | 2026-07-25 |
| E-P7-005 | 7 | Approved and merged patient interface | GitHub pull request #6 | 2026-07-26 |
| E-P8-001 | 8 | Administrator resources, workspace, and authorization | `backend/app/routes/admin.py`, `frontend/src/pages/AdminPage.tsx` | 2026-07-26 |
| E-P8-002 | 8 | Staged validation, diff, publication, retention, and rollback service | `backend/app/services/knowledge_admin_service.py` | 2026-07-26 |
| E-P8-003 | 8 | Authorization, invalid archive, publish, restart, frozen-history, and rollback tests | Phase 8 completion report | 2026-07-26 |
| E-P8-004 | 8 | Administration guide and retained publication decision | `docs/administration.md`, ADR 0007 | 2026-07-26 |
| E-P8-005 | 8 | Approved and merged administration implementation | GitHub pull request #7 | 2026-07-26 |
| E-P9-001 | 9 | Immutable report persistence, secure resources, and PDF composer | `backend/app/services/report_service.py` | 2026-07-26 |
| E-P9-002 | 9 | PDF, ownership, repeatability, long-content, history, and audit tests | Phase 9 completion report | 2026-07-26 |
| E-P9-003 | 9 | Extracted-text and rendered-page PDF inspection | Phase 9 completion report | 2026-07-26 |
| E-P9-004 | 9 | Report architecture and snapshot-generation methodology | `docs/reports-and-history.md`, ADR 0008 | 2026-07-26 |
| E-P10-001 | 10 | Cross-layer patient, role-boundary, and security-negative scenarios | `backend/tests/test_defence_demo.py` | 2026-07-26 |
| E-P10-002 | 10 | React accessibility, stale-state, and API-failure recovery scenarios | `frontend/src/App.test.tsx` | 2026-07-26 |
| E-P10-003 | 10 | Executable requirement-to-test completeness evidence | `docs/requirements-to-test-report.md`, `backend/tests/test_quality_evidence.py` | 2026-07-26 |
| E-P10-004 | 10 | Reproducible full local verification command | `scripts/verify-phase10.ps1` | 2026-07-26 |
| E-P10-005 | 10 | Full gate, migration cycle, live health, and browser smoke evidence | `docs/phase-reports/phase-10.md` | 2026-07-26 |
| E-P11-001 | 11 | Threat-model-led baseline security review and closure candidates | Codex Security scan and Phase 11 report | 2026-07-26 |
| E-P11-002 | 11 | Request, session, privilege, upload, audit, and privacy controls | `backend/app/`, `backend/tests/test_security.py` | 2026-07-26 |
| E-P11-003 | 11 | Verified backup, restore, retention, and deletion operations | `backend/app/commands.py` | 2026-07-26 |
| E-P11-004 | 11 | Python and frontend production dependency review | `scripts/verify-phase11.ps1` | 2026-07-26 |
| E-P11-005 | 11 | Security, privacy, residual-risk, and methodology documentation | `docs/security-and-privacy.md`, Phase 11 methodology and report | 2026-07-26 |
| E-P12-001 | 12 | Windows runtime, maintenance, and persistence implementation | `backend/app/runtime.py`, `backend/app/launcher.py`, `backend/app/maintenance.py` | 2026-07-27 |
| E-P12-002 | 12 | Windows build specification, archive, and checksum process | `packaging/windows/`, `scripts/build-windows-release.ps1` | 2026-07-27 |
| E-P12-003 | 12 | Persistent non-root Docker/Linux server release | `Dockerfile`, `compose.server.yml`, `backend/app/server.py` | 2026-07-27 |
| E-P12-004 | 12 | Runtime path, secret, routing, locking, backup, restore, reset, and diagnostics tests | `backend/tests/test_runtime.py` | 2026-07-27 |
| E-P12-005 | 12 | Local/server deployment decision and operator guidance | `docs/windows-release.md`, `docs/server-deployment.md`, ADR 0009 | 2026-07-27 |
| E-P13-001 | 13 | Complete patient, API, troubleshooting, and architecture reader set | `docs/user-guide.md`, `docs/api-reference.md`, `docs/troubleshooting.md`, `docs/architecture/diagrams.md` | 2026-07-27 |
| E-P13-002 | 13 | Evidence-led adaptable academic manuscript and methodology | `docs/academic-report.md`, `docs/academic/phase-13-methodology.md` | 2026-07-27 |
| E-P13-003 | 13 | Executable document, link, heading, index, and source validation | `scripts/validate_documentation.py`, `scripts/verify-phase13.ps1` | 2026-07-27 |
| E-P13-004 | 13 | Consolidated traceability and completion evidence | `docs/requirements-to-test-report.md`, `docs/phase-reports/phase-13.md` | 2026-07-27 |
| E-P13-005 | 13 | Non-sensitive public application screenshot | `docs/images/landing-page.png` | 2026-07-27 |

External screenshots and large artifacts may be mirrored in the project Google Drive. Each external item must retain a stable filename or link and must not contain patient data or secrets.
