# Inference Engine Guide

## Purpose and boundary

The Phase 5 engine evaluates validated consultation facts against one immutable
`KnowledgePackage`. It provides transparent educational guidance; it does not diagnose,
prescribe, calculate disease probability, or replace an eye examination.

The primary interface is:

```python
result = inference_engine.evaluate(knowledge_package, facts)
```

The engine is stateless. It does not persist or log facts, modify the knowledge snapshot,
or depend on Flask request state. Consultation orchestration and API exposure begin in Phase 6.

## Fact validation

Facts are an object keyed by stable symptom IDs. The engine rejects unknown IDs, `null`,
incorrect exact types, out-of-range integers, and unsupported choice values. An unanswered
fact must be omitted. Python booleans are not accepted as integers, and caller input is never
mutated.

## Three-valued evaluation

An omitted fact is `UNKNOWN`, not `FALSE`. Strong-Kleene logic is used:

| Expression | TRUE | FALSE | UNKNOWN |
|---|---|---|---|
| `AND` | every child is true | any child is false | otherwise |
| `OR` | any child is true | every child is false | otherwise |
| `NOT` | child is false | child is true | child is unknown |

A missing exclusion therefore cannot satisfy `NOT`. A confirmed emergency rule may still
match even while unrelated rules remain pending.

## Deterministic processing

Rules are evaluated by descending authored priority and then stable rule ID. Each eligible
rule fires once. The current schema produces conclusions rather than new facts, so the fixed
point is reached after one finite pass. Adding another valid JSON rule requires no Python
change.

Every rule is `matched`, `unmatched`, or `pending`. No-match results are deliberately neutral:
no risk level, indication, recommendation, or reassurance is invented.

## Safety conflict resolution

Overall risk is the highest authored rank among matched rules. Priority orders rules within a
tier and can never override higher risk. Recommendations are emitted only from matched rules
at the highest tier, preventing routine advice from diluting urgent instructions. Lower-tier
matches remain visible as possible indications and in the trace.

Conditions, recommendations, and evidence are deduplicated by stable ID. Matched urgent and
emergency rules are also exposed as red flags.

## Match score and explainability

Each rule reports total authored leaf criteria, known criteria, satisfied criteria, and the
satisfied percentage. This describes rule coverage only. It is not used for safety ordering
and is never a diagnostic probability or clinical confidence score.

The result includes the package identity, outcome and completeness states, risk, matched and
pending rules, indications, highest-tier recommendations, red flags, missing facts, evidence,
full trace, disclaimer, and score notice. Trace nodes record stable paths, operators, expected
and available actual values, missing state, and truth. Serialization uses no timestamp or
random identifier.

## Local demonstration

Use only non-sensitive demonstration facts:

```powershell
cd backend
.venv\Scripts\python -m flask --app run.py inference-evaluate `
  --facts-file examples\demo-facts-emergency.json --json
```

Invalid facts return a non-zero exit code and stable field-level issue codes.
