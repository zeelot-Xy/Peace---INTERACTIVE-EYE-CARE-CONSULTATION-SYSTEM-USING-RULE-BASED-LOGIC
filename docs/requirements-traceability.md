# Requirements Traceability Matrix

| ID | Requirement | Phase | Implementation | Verification | Status |
|---|---|---:|---|---|---|
| GOV-001 | Use approval-gated development phases | 1 | Contribution guide and phase reports | Documentation review | Implemented |
| ARC-001 | Use a layered React and Flask architecture | 1 | Frontend, API routes, and services | Build and baseline tests | Implemented |
| API-001 | Expose versioned REST endpoints | 1 | `/api/v1/health` | Backend API tests | Implemented |
| CFG-001 | Support development, testing, production, and packaged profiles | 1 | Flask configuration module | Application-factory tests | Implemented |
| DOC-001 | Maintain technical and academic documentation during every phase | 1 | `docs/` documentation system | Documentation review | Implemented |
| SAFE-001 | State that the system is non-diagnostic | 1 | UI, README, and architecture documentation | Frontend tests | Implemented |
| DEP-001 | Provide reproducible Docker development configuration | 1 | Dockerfiles and Compose | Image builds and live service checks | Implemented |
| DB-201 | Persist application data in SQLite with controlled migrations | 2 | SQLAlchemy models and Alembic revision | Migration and schema tests | Implemented |
| AUTH-201 | Register and authenticate patients securely | 2 | Auth service, APIs, and minimal React forms | Backend and frontend tests | Implemented |
| AUTH-202 | Protect browser sessions with cookie JWTs and CSRF | 2 | JWT configuration and Axios interceptors | CSRF, rotation, and replay tests | Implemented |
| AUTH-203 | Revoke current and all user sessions | 2 | Token families and revocation records | Logout and password-change tests | Implemented |
| AUTH-204 | Enforce patient and administrator roles | 2 | Role decorator and administrator users API | Authorization tests | Implemented |
| AUTH-205 | Bootstrap administrators without default secrets | 2 | Interactive Flask CLI command | CLI and documentation review | Implemented |
| DOC-201 | Document Phase 2 architecture, privacy, and methodology | 2 | Database, authentication, and academic notes | Documentation review | Implemented |
| KB-301 | Store expert knowledge in immutable semantic-versioned JSON packages | 3 | `backend/knowledge/packages/eye-care-en-1.0.0` | Manifest and package tests | Implemented |
| KB-302 | Validate knowledge using formal machine-readable contracts | 3 | Eight Draft 2020-12 schemas and authoring validator | Schema-positive and negative tests | Implemented |
| KB-303 | Trace every medical assertion to a published source | 3 | Source registry and `citation_ids` | Citation coverage and reference tests | Implemented |
| KB-304 | Represent common, chronic-risk, and emergency adult eye pathways | 3 | 15 conditions and 21 rules | Scope and emergency-rule tests | Implemented |
| SAFE-301 | Prevent diagnostic, prescribing, and unsafe-delay wording | 3 | Safety policy and prohibited-wording validator | Negative wording test and manual review | Implemented |
| SAFE-302 | Preserve deterministic safety escalation | 3 | Fixed four-level risk ranks and emergency priority band | Risk-order and emergency-evidence tests | Implemented |
| DOC-301 | Document knowledge authoring, evidence, rule language, safety, and methodology | 3 | Phase 3 documentation set and ADR 0002 | Documentation review | Implemented |
| KB-401 | Load a configured package into a deeply immutable runtime snapshot | 4 | `app/knowledge` contracts and manager | Loader, immutability, and factory tests | Implemented |
| KB-402 | Reject malformed, incompatible, incomplete, or unsafe packages deterministically | 4 | Shared runtime validator and validation report | Table-driven negative and deterministic-report tests | Implemented |
| KB-403 | Cache unchanged packages and invalidate changes safely | 4 | Metadata signatures and SHA-256 fingerprints | Identity, change, and forced-reload tests | Implemented |
| SAFE-401 | Preserve the last valid snapshot and fail closed without initial knowledge | 4 | Atomic activation and startup integration | Failed-activation and startup-failure tests | Implemented |
| OPS-401 | Expose non-HTTP package validation and status operations | 4 | Flask and authoring CLI commands | CLI JSON and exit-code tests | Implemented |
| DOC-401 | Document loading, recovery, architecture, evaluation, and methodology | 4 | Runtime guide, ADR 0003, and Phase 4 methodology | Documentation review | Implemented |
| INF-501 | Evaluate authored rules deterministically without Python rule logic | 5 | `app/inference` stateless engine | Every-rule and runtime-extension scenarios | Implemented |
| INF-502 | Preserve incomplete facts with nested three-valued logic | 5 | Recursive expression evaluator | Operator and truth-table tests | Implemented |
| INF-503 | Produce transparent repeatable outcomes and traces | 5 | Immutable inference contracts | Stable JSON and repeatability tests | Implemented |
| SAFE-501 | Let highest safety risk prevail and prevent advice dilution | 5 | Risk aggregation and tier filtering | Conflict and suppression tests | Implemented |
| SAFE-502 | Reject invalid facts and authored operands | 5 | Fact normalizer and semantic validation | Type, boundary, choice, and operand tests | Implemented |
| OPS-501 | Evaluate non-sensitive demonstration facts locally | 5 | `inference-evaluate` CLI | CLI JSON and failure tests | Implemented |
| DOC-501 | Document inference semantics, limitations, and methodology | 5 | Engine guide, ADR 0004, methodology, and report | Documentation review | Implemented |
| CON-601 | Start, autosave, resume, revise, complete, and cancel consultations | 6 | Consultation service and REST resources | Lifecycle service/API tests | Implemented |
| CON-602 | Present one applicable question at a time with progress and skip behavior | 6 | Ordered state, branching, and optional skips | Branch, progress, and skip tests | Implemented |
| CON-603 | Freeze knowledge for reproducible sessions and results | 6 | Package identity fields and result snapshot | Persistence and result tests | Implemented |
| CON-604 | Prevent concurrent answer loss | 6 | Monotonic revision checks | Stale-write conflict test | Implemented |
| SAFE-601 | Prevent branching or manipulation from bypassing red flags | 6 | Mandatory safety applicability and completion checks | Safety branch and emergency tests | Implemented |
| API-601 | Expose owned consultation, history, and result resources | 6 | `/api/v1/consultations` blueprint | Authentication and ownership tests | Implemented |
| DOC-601 | Document lifecycle APIs, safety, privacy, and methodology | 6 | API guide, ADR 0005, methodology, and report | Documentation review | Implemented |
| UI-701 | Provide a responsive authenticated patient shell and dashboard | 7 | React navigation, dashboard, responsive and dark themes | Semantic frontend tests and browser inspection | Implemented |
| UI-702 | Present one applicable question at a time with progress and revision | 7 | Consultation page and API client | Autosave and question-flow tests | Implemented |
| UI-703 | Provide consultation history, results, and printable report views | 7 | History and result pages | Result-separation and source-link tests | Implemented |
| SAFE-701 | Communicate urgent action prominently and keep indications non-diagnostic | 7 | Safety alert and structured result hierarchy | Alert and wording tests | Implemented |
| ACC-701 | Support keyboard, semantic, responsive, and light/dark operation | 7 | Native controls, landmarks, focus, mobile navigation, theme styles | Semantic tests and manual inspection | Implemented |
| DOC-701 | Document the patient journey, accessibility, privacy, and methodology | 7 | Interface guide, ADR 0006, methodology, and report | Documentation review | Implemented |
| ADM-801 | Restrict operational administration to administrators | 8 | Admin role guard, routes, and workspace | Backend and frontend authorization tests | Implemented |
| ADM-802 | Summarize users, consultations, stored reports, and audit activity | 8 | Administrator reporting service and React workspace | API and semantic interface tests | Implemented |
| KB-801 | Validate and preview complete uploaded knowledge packages | 8 | Staged ZIP inspection, shared validator, collection diff, affected-rule preview | Valid, invalid, duplicate, and diff tests | Implemented |
| KB-802 | Publish only valid packages and preserve prior versions | 8 | Retained directories, version records, atomic manager activation | Publish and frozen-consultation tests | Implemented |
| KB-803 | Support audited rollback and restart restoration | 8 | Fingerprint-protected state file and rollback service | Restart, rollback, and audit tests | Implemented |
| DOC-801 | Document administration, knowledge governance, recovery, and methodology | 8 | Admin guide, ADR 0007, methodology, and report | Documentation review | Implemented |
| REP-901 | Generate a printable and downloadable completed consultation report | 9 | Report service, ReportLab composer, and patient controls | PDF and frontend tests | Implemented |
| REP-902 | Keep repeated reports reproducible and tied to frozen knowledge | 9 | Stored composition snapshot, exact PDF bytes, checksum, and one-report constraint | Repeat-generation and migration tests | Implemented |
| REP-903 | Enforce secure patient ownership and governed administrator review | 9 | Report resource ownership query and role claim | Privacy and administrator tests | Implemented |
| HIS-901 | Filter patient history by status, risk, and date | 9 | Authenticated server filters and React controls | API and frontend tests | Implemented |
| DOC-901 | Document report architecture, privacy, API, testing, and methodology | 9 | Report guide, ADR 0008, methodology, and report | Documentation review | Implemented |
