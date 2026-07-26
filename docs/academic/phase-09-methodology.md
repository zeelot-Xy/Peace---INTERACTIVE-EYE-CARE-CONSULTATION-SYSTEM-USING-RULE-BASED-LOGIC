# Phase 9 Methodology: Reproducible Reports and Historical Retrieval

Phase 9 used snapshot-based document generation to preserve the relationship between a
consultation, its rule-based inference result, and its published evidence. Report composition
does not execute current rules. Instead, it reads the completed result snapshot, resolves the
fingerprint-verified frozen knowledge package for question wording, and captures patient
details at the moment of generation.

The document generator applies a fixed A4 information hierarchy: safety limitation, patient
context, action level, warning signs, recommendations, possible indications, recorded
responses, rule explanation, cited sources, and knowledge provenance. This hierarchy supports
defence demonstration by making rule outputs traceable while maintaining the non-diagnostic
boundary. Unicode-capable embedded fonts, repeated table headings, and automatic pagination
support varied names and long consultations.

Evaluation combined ownership and administrator-access tests, idempotent-generation checks,
PDF byte and extracted-text checks, Unicode and missing-profile cases, long multi-page output,
server-side history filters, audit evidence, migration repeatability, frontend interaction
tests, and rendered-page visual inspection. A SHA-256 checksum verifies the retained artifact,
but it is an integrity identifier rather than a digital signature.

The method improves reproducibility and explainability, but the PDF remains an output of an
unvalidated academic knowledge base. It must not be interpreted as a diagnosis, clinical
record, prescription, or substitute for examination by a qualified eye-care professional.
