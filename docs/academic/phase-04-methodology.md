# Phase 4 Methodology: Runtime Knowledge Validation

## Method

Phase 4 applied defensive data-loading and snapshot-isolation techniques to the documentary knowledge created in Phase 3. One validation implementation serves offline authoring and the Flask runtime, reducing the risk that a package accepted by one path is rejected or interpreted differently by another.

Validation proceeds from least trusted to most trusted material. The manifest schema is checked before its file declarations are followed. Each declared document is then checked structurally and semantically, followed by integrity, version, identity, cross-reference, evidence, wording, and risk-order controls. Unsupported schema versions are rejected explicitly rather than interpreted optimistically.

## Reliability design

Validated JSON is recursively converted to immutable mappings and tuples. Stable ID indexes make later rule-engine access deterministic without changing source documents. Candidate construction occurs before a locked active-reference exchange, implementing a last-known-valid strategy. When a candidate fails, the report is retained for explanation while the existing snapshot remains available.

A canonical SHA-256 fingerprint identifies package content. CRLF is normalized to LF before hashing because Git may materialize text differently on Windows and Linux; logical JSON content therefore produces the same integrity result in local and container environments.

## Evaluation

Positive, negative, integration, CLI, and concurrency tests cover valid loading, missing and malformed files, invalid schemas, duplicates, broken references, checksums, version incompatibility, incomplete collections, deterministic issue order, cache behavior, forced reload, last-valid preservation, startup failure, deep immutability, and simultaneous reads.

## Limitation

Runtime validation demonstrates technical consistency, not clinical validity. The package remains a draft academic knowledge artefact. Phase 4 does not evaluate rules or infer a condition, recommendation, or risk. Clinical expert review remains unavailable and is documented as a project limitation.

