# Requirements-to-Test Evidence Report

This report supplements the requirements traceability matrix with concrete automated test
locations and review evidence. `backend/tests/test_quality_evidence.py` fails when any matrix
requirement is absent from this report.

| Requirements | Primary automated evidence | Additional evidence |
|---|---|---|
| `GOV-001`, `DOC-001` | `test_quality_evidence.py` | Phase reports and approval-gated Git history |
| `ARC-001`, `API-001`, `CFG-001`, `DEP-001` | `test_health.py`, `test_config.py` | Production build and Compose configuration |
| `SAFE-001` | `App.test.tsx` landing-page safety test | README and architecture review |
| `DB-201` | `test_models.py`, migration cycle | Database and migration guide |
| `AUTH-201`, `AUTH-202`, `AUTH-203`, `AUTH-204`, `AUTH-205` | `test_auth.py`, `test_defence_demo.py`, `App.test.tsx` | Authentication sequence and administrator bootstrap guide |
| `DOC-201` | `test_quality_evidence.py` | Phase 2 methodology and completion report |
| `KB-301`, `KB-302`, `KB-303`, `KB-304` | `test_knowledge_package.py` | Schemas, source register, and authored package |
| `SAFE-301`, `SAFE-302` | `test_knowledge_package.py`, `test_inference_engine.py` | Knowledge safety and scope review |
| `DOC-301` | `test_quality_evidence.py` | Phase 3 methodology and ADR 0002 |
| `KB-401`, `KB-402`, `KB-403`, `SAFE-401`, `OPS-401` | `test_knowledge_manager.py` | Runtime guide and CLI evidence |
| `DOC-401` | `test_quality_evidence.py` | Phase 4 methodology and ADR 0003 |
| `INF-501`, `INF-502`, `INF-503` | `test_inference_engine.py`, `test_inference_expressions.py` | Stable inference contracts and traces |
| `SAFE-501`, `SAFE-502`, `OPS-501` | `test_inference_facts.py`, `test_inference_cli.py` | Safety-first resolution and CLI guide |
| `DOC-501` | `test_quality_evidence.py` | Phase 5 methodology and ADR 0004 |
| `CON-601`, `CON-602`, `CON-603`, `CON-604` | `test_consultations.py`, `test_defence_demo.py` | Consultation API guide |
| `SAFE-601`, `API-601` | `test_consultations.py`, `test_defence_demo.py` | Patient safety-path demonstration |
| `DOC-601` | `test_quality_evidence.py` | Phase 6 methodology and ADR 0005 |
| `UI-701`, `UI-702`, `UI-703` | `App.test.tsx` | Responsive patient-journey inspection |
| `SAFE-701`, `ACC-701` | `App.test.tsx` urgent, semantic, keyboard, and recovery tests | Manual light/dark and mobile inspection |
| `DOC-701` | `test_quality_evidence.py` | Phase 7 methodology and ADR 0006 |
| `ADM-801`, `ADM-802` | `test_admin.py`, `test_defence_demo.py`, `App.test.tsx` | Administrator governance demonstration |
| `KB-801`, `KB-802`, `KB-803` | `test_admin.py`, `test_knowledge_manager.py` | Retained package directories and state file |
| `DOC-801` | `test_quality_evidence.py` | Phase 8 methodology and ADR 0007 |
| `REP-901`, `REP-902`, `REP-903` | `test_reports.py`, `test_defence_demo.py`, `App.test.tsx` | Extracted-text and rendered-page review |
| `HIS-901` | `test_reports.py`, `App.test.tsx` | Filtered-history browser review |
| `DOC-901` | `test_quality_evidence.py` | Phase 9 methodology and ADR 0008 |
| `VER-1001` | `verify-phase10.ps1`, all backend and frontend suites | Coverage, lint, build, migration, and hygiene outputs |
| `E2E-1001` | `test_defence_demo.py`, `App.test.tsx` | Patient safety-path demonstration and Administrator governance demonstration |
| `TRC-1001` | `test_quality_evidence.py` | This evidence report and the traceability matrix |
| `ACC-1001` | `App.test.tsx` accessible-name, error recovery, stale revision, and report failure tests | Live keyboard and responsive review |
| `DOC-1001` | `test_quality_evidence.py` | Phase 10 methodology, testing guide, defence guide, and completion report |
| `SEC-1101`, `SEC-1102` | `test_security.py`, `test_config.py` | Request, headers, CORS, media-type, rate-limit, and normalization evidence |
| `SEC-1103` | `test_auth.py`, `test_security.py` | Atomic refresh and current administrator-role review |
| `SEC-1104` | `test_admin.py`, `test_security.py` | Bounded archive and immutable publication review |
| `PRIV-1101`, `PRIV-1102` | `test_security.py` | Audit redaction, immutability, retention, backup, and restore evidence |
| `DEP-1101` | `verify-phase11.ps1` | Python and npm production advisory checks |
| `DOC-1101` | `test_quality_evidence.py` | Phase 11 security guide, methodology, and completion report |
| `PKG-1201`, `PKG-1202` | `test_runtime.py`, `verify-phase12.ps1` | PyInstaller build, first-run/restart smoke test, and Windows release guide |
| `OPS-1201` | `test_runtime.py` | Port, lock, migration, backup, restore, reset, and diagnostics scenarios |
| `DEP-1201` | `verify-phase12.ps1` | Compose validation, Docker build, health, restart, and volume persistence |
| `DOC-1201` | `test_quality_evidence.py` | ADR 0009, Windows/server guides, methodology, and completion report |

## Gate commands

The canonical Windows command is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-phase12.ps1
```

It runs Git whitespace validation, Ruff, pytest with a 90% minimum application-coverage gate,
ESLint, Vitest, TypeScript, the Vite production build, Python dependency compatibility and
vulnerability review, the npm production dependency audit, and server Compose validation.
Passing `-IncludeHeavyBuilds` additionally creates and smokes the Windows release once, then
builds, starts, restarts, and verifies persistent data in an isolated Docker server project.

## Interpretation

Passing tests demonstrate that the authored software behaves according to its documented
contracts for the tested scenarios. They do not demonstrate clinical effectiveness, clinical
safety validation, or diagnostic accuracy.
