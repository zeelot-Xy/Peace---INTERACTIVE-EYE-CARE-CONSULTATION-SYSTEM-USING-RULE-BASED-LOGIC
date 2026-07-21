# Knowledge Authoring Guide

## Purpose

The knowledge package is an inspectable academic artefact, not a clinically validated medical product. It provides educational possible-indication and escalation content for adults. Authors must never add diagnostic declarations, prescriptions, medication doses, or advice that delays urgent care.

## Package layout

Each immutable package lives under `backend/knowledge/packages/<package-id>/`. Package `eye-care-en-1.0.0` contains a manifest plus sources, symptoms/facts, questions, conditions, recommendations, risk levels, and rules. The corresponding Draft 2020-12 contracts live in `backend/knowledge/schemas/`.

Stable IDs use lowercase snake case and a namespace prefix such as `fact_`, `question_`, `condition_`, `recommendation_`, `risk_`, `rule_`, or `source_`. Never reuse an ID for a different meaning. Meaningful changes require a new semantic content version and a new package directory.

## Authoring workflow

1. Define the supported population and exclusions in the manifest.
2. Add authoritative sources before adding assertions. Prefer WHO, national health ministries, government public-health agencies, and specialist public institutions.
3. Add facts and questions with source citations. Mark red-flag questions as `safety_critical`.
4. Add possible-indication descriptions using cautious language and an explicit limitation.
5. Add recommendations that state an appropriate care action without diagnosing or prescribing.
6. Add rules with evidence, rationale, explanation text, priority, risk, and references.
7. Recalculate each content-file SHA-256 value in the manifest.
8. Run the validator and tests before review.

```powershell
cd backend
.venv\Scripts\python tools\validate_knowledge_package.py --json
.venv\Scripts\python -m pytest tests/test_knowledge_package.py
```

## Evidence rules

Every symptom description, question, possible indication, recommendation, risk action, and rule must include at least one source ID. Emergency rules require at least two sources and a priority of 900 or higher. A source record contains the organization, page title, HTTPS URL, verified date when one is displayed, retrieval date, and the claims it supports.

Do not copy long passages from a source. Paraphrase the supported fact and record provenance. A link becoming unavailable is a review issue; it does not justify silently replacing the record with an unsupported claim.

## Review checklist

- Scope remains adults aged 18 and older and English-language.
- Pediatric, pregnancy-specific, image interpretation, medication, diagnostic, and prescribing logic is absent.
- New and changed claims have traceable sources.
- Safety escalation wins over common-condition matching.
- IDs are unique and all references resolve.
- The manifest content version matches every file and every checksum matches.
- Validator, Ruff, and pytest pass.
- A reviewer reads user-facing wording before a package is marked reviewed or published.

Phase 3 validates authored files during development. Runtime loading, cached fallback, administrative upload, publishing, and rollback belong to Phases 4 and 8.
