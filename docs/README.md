# Documentation Index

Repository documentation is versioned with the implementation. Collaborative academic drafts, review comments, presentation assets, and large evidence files may be mirrored in Google Drive, but accepted technical truth remains here.

## Final reader set

- [`client-handoff.md`](client-handoff.md) — client delivery inventory, acceptance, transfer,
  backup, and support procedure
- [`final-audit-checklist.md`](final-audit-checklist.md) — final implementation and delivery
  audit
- [`demo-data-and-credentials.md`](demo-data-and-credentials.md) — fictional demonstration data
  and no-default-credential procedure
- [`presentation-outline.md`](presentation-outline.md) — fourteen-slide defence narrative and
  likely questions
- [`user-guide.md`](user-guide.md) — patient operation and result interpretation
- [`administration.md`](administration.md) — administrator governance and knowledge operations
- [`api-reference.md`](api-reference.md) — consolidated versioned REST contract
- [`architecture/diagrams.md`](architecture/diagrams.md) — architecture and defence diagrams
- [`troubleshooting.md`](troubleshooting.md) — development, Windows, server, and recovery support
- [`academic-report.md`](academic-report.md) — complete adaptable final-year manuscript
- [`academic-report-outline.md`](academic-report-outline.md) — institution-format transfer
  checklist
- [`academic/phase-13-methodology.md`](academic/phase-13-methodology.md) — evidence-led
  documentation synthesis
- [`phase-reports/phase-13.md`](phase-reports/phase-13.md) — Phase 13 completion record
- [`academic/phase-14-methodology.md`](academic/phase-14-methodology.md) — final release audit
  methodology
- [`phase-reports/phase-14.md`](phase-reports/phase-14.md) — final audit and handoff record

## Governance and engineering

- [`architecture/overview.md`](architecture/overview.md) — system boundaries and layered design
- [`adr/0001-layered-json-knowledge-architecture.md`](adr/0001-layered-json-knowledge-architecture.md) — foundational architecture decision
- [`development.md`](development.md) — setup and verification
- [`testing.md`](testing.md) — test strategy
- [`database.md`](database.md) — data dictionary and migration operations
- [`authentication.md`](authentication.md) — authentication, API, CSRF, and administrator bootstrap
- [`knowledge-authoring.md`](knowledge-authoring.md) — safe package authoring and review workflow
- [`knowledge-schema-reference.md`](knowledge-schema-reference.md) — JSON collection contracts and invariants
- [`rule-language.md`](rule-language.md) — declarative rule expression language
- [`inference-engine.md`](inference-engine.md) — tri-state evaluation, safety conflicts, scores, traces, and CLI
- [`consultation-api.md`](consultation-api.md) — lifecycle resources, branching, concurrency, safety, and reproducibility
- [`patient-interface.md`](patient-interface.md) — patient journey, accessibility, safety, recovery, and privacy
- [`administration.md`](administration.md) — administrator resources, knowledge publishing, rollback, and recovery
- [`reports-and-history.md`](reports-and-history.md) — immutable PDFs, secure downloads, history filters, and privacy
- [`knowledge-scope-and-safety.md`](knowledge-scope-and-safety.md) — supported population and safety policy
- [`source-register.md`](source-register.md) — published evidence catalogue
- [`port-registry.md`](port-registry.md) — reserved localhost ports and release policy
- [`requirements-traceability.md`](requirements-traceability.md) — requirement-to-evidence mapping
- [`requirements-to-test-report.md`](requirements-to-test-report.md) — concrete automated evidence for every implemented requirement
- [`defence-demo.md`](defence-demo.md) — repeatable patient and administrator defence demonstration
- [`evidence-register.md`](evidence-register.md) — durable evidence index
- [`security-and-privacy.md`](security-and-privacy.md) — controls, threat boundaries, retention,
  backup, restore, deletion, and residual risks

- [`knowledge-runtime.md`](knowledge-runtime.md) — runtime loading, cache, activation, CLI, and recovery
- [`adr/0003-atomic-runtime-knowledge-snapshots.md`](adr/0003-atomic-runtime-knowledge-snapshots.md) — fail-closed atomic snapshot decision
- [`academic/phase-04-methodology.md`](academic/phase-04-methodology.md) — defensive runtime loading and snapshot isolation
- [`phase-reports/phase-04.md`](phase-reports/phase-04.md) — Phase 4 completion record
- [`adr/0004-tristate-safety-first-inference.md`](adr/0004-tristate-safety-first-inference.md) — incomplete-fact and risk-resolution decision
- [`academic/phase-05-methodology.md`](academic/phase-05-methodology.md) — rule-based inference methodology
- [`phase-reports/phase-05.md`](phase-reports/phase-05.md) — Phase 5 completion record
- [`adr/0005-version-frozen-consultation-lifecycle.md`](adr/0005-version-frozen-consultation-lifecycle.md) — consultation state and reproducibility decision
- [`academic/phase-06-methodology.md`](academic/phase-06-methodology.md) — stateful consultation methodology
- [`phase-reports/phase-06.md`](phase-reports/phase-06.md) — Phase 6 completion record
- [`adr/0006-accessible-safety-first-patient-interface.md`](adr/0006-accessible-safety-first-patient-interface.md) — patient interaction and risk-communication decision
- [`academic/phase-07-methodology.md`](academic/phase-07-methodology.md) — patient interaction-design methodology
- [`phase-reports/phase-07.md`](phase-reports/phase-07.md) — Phase 7 completion record
- [`adr/0007-retained-atomic-knowledge-publication.md`](adr/0007-retained-atomic-knowledge-publication.md) — retained package and atomic publication decision
- [`academic/phase-08-methodology.md`](academic/phase-08-methodology.md) — administrative governance methodology
- [`phase-reports/phase-08.md`](phase-reports/phase-08.md) — Phase 8 completion record
- [`adr/0008-database-retained-immutable-pdf-reports.md`](adr/0008-database-retained-immutable-pdf-reports.md) — report reproducibility and storage decision
- [`academic/phase-09-methodology.md`](academic/phase-09-methodology.md) — snapshot document-generation methodology
- [`phase-reports/phase-09.md`](phase-reports/phase-09.md) — Phase 9 completion record
- [`academic/phase-10-methodology.md`](academic/phase-10-methodology.md) — requirements-based comprehensive verification methodology
- [`phase-reports/phase-10.md`](phase-reports/phase-10.md) — Phase 10 completion record
- [`academic/phase-11-methodology.md`](academic/phase-11-methodology.md) — threat-model-led
  security and privacy methodology
- [`phase-reports/phase-11.md`](phase-reports/phase-11.md) — Phase 11 completion record

## Packaging and deployment

- [`windows-release.md`](windows-release.md) — client startup, data, maintenance, and build guide
- [`server-deployment.md`](server-deployment.md) — persistent Docker/Linux deployment and HTTPS
- [`adr/0009-dual-local-and-server-release.md`](adr/0009-dual-local-and-server-release.md) —
  local and hosted delivery decision
- [`academic/phase-12-methodology.md`](academic/phase-12-methodology.md) — release methodology
- [`phase-reports/phase-12.md`](phase-reports/phase-12.md) — Phase 12 completion record

## Project delivery

- [`academic-report-outline.md`](academic-report-outline.md) — evolving final-year report structure
- [`academic/phase-02-methodology.md`](academic/phase-02-methodology.md) — persistence and authentication methodology
- [`academic/phase-03-methodology.md`](academic/phase-03-methodology.md) — documentary acquisition and knowledge representation
- [`collaboration-workflow.md`](collaboration-workflow.md) — Git, Drive, and Slack responsibilities
- [`phase-reports/phase-01.md`](phase-reports/phase-01.md) — Phase 1 completion record
- [`phase-reports/phase-02.md`](phase-reports/phase-02.md) — Phase 2 completion record
- [`phase-reports/phase-03.md`](phase-reports/phase-03.md) — Phase 3 completion record
