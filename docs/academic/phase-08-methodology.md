# Phase 8 Methodology: Administrative Governance

Phase 8 applied role-based access control and immutable-version governance to operational
administration. The administrator interface was treated as a control surface rather than a
source of expert logic: it summarizes persisted records, displays audit evidence, and invokes
backend services that retain all validation and publication decisions.

Knowledge updates use a staged transaction model. A bounded ZIP archive is inspected for
inventory and path safety, extracted outside the active directory, passed through the Phase 4
structural, referential, checksum, evidence, and wording validator, and compared with the
currently active immutable snapshot. The comparison reports added, changed, and removed IDs
per collection and derives affected rules through rule references. A valid candidate is
retained, but activation remains a separate explicit administrator action.

Publication and rollback use the same revalidation and atomic activation path. Database records,
audit events, retained package directories, and a fingerprint-protected state pointer provide
traceability across restart. Evaluation combined authorization tests, invalid-archive tests,
publish/rollback tests, restart restoration, frozen-consultation reproduction, semantic
frontend tests, migration checks, linting, and production compilation.

This process improves technical accountability but does not constitute clinical review or
medical-device validation. The administrator cannot remove the mandatory disclaimer or bypass
the authored knowledge safety validator.
