# Phase 3 Academic Methodology Notes

## Knowledge acquisition

Phase 3 used documentary knowledge acquisition because direct clinical expert review was unavailable. Candidate assertions were restricted to public material from the World Health Organization, Nigeria's Federal Ministry of Health and Social Welfare, the National Eye Institute, the Centers for Disease Control and Prevention, and the National Health Service. Each authored assertion references a machine-readable source record, and the limitation of absent clinical validation is retained explicitly.

The first scope was purposefully bounded to English-speaking adults. It includes common eye concerns, chronic sight-threatening risk pathways, and urgent red-flag patterns. Pediatric, pregnancy-specific, imaging, diagnostic, medication, and prescribing domains were excluded to reduce unsupported inference and keep the prototype's evaluation defensible.

## Knowledge representation

The system represents knowledge as versioned JSON rather than procedural code. Normalized facts describe questionnaire answers. Declarative rules combine fact predicates with AND, OR, and NOT structures, priorities, possible-indication conclusions, safety risk, recommendations, rationale, and citations. This design prepares for forward chaining while keeping the source of each conclusion visible.

Risk is ordinal rather than probabilistic: routine, prompt, urgent, and emergency. Rule priority controls evaluation preference, while risk rank controls safety escalation. The planned rule-match score is not a probability and must not be described as diagnostic confidence.

## Quality and safety method

Draft 2020-12 schemas constrain each collection and reject unknown properties. A deterministic authoring validator checks schema conformance, semantic-version consistency, IDs, cross-references, SHA-256 integrity, citation presence, emergency evidence, prohibited wording, and fixed risk order. Negative tests deliberately introduce checksum tampering, a broken reference, diagnostic wording, and an invalid risk rank to demonstrate failure detection.

This validation establishes structural and provenance quality, not clinical validity. Later evaluation must separately test inference completeness, conflict resolution, consultation safety, accessibility, and expert review where available.
