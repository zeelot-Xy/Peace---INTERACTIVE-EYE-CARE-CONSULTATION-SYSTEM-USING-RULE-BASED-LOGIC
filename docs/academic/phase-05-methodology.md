# Phase 5 Methodology: Rule-Based Inference

## Method

Phase 5 used a production-rule approach in which domain knowledge remains in versioned JSON
while a general Python interpreter evaluates it. Consultation observations are normalized into
typed facts and recursively compared with authored predicates.

Incomplete information uses strong-Kleene three-valued logic. This avoids the unsafe
closed-world assumption that an unanswered symptom is absent. Recursive `AND`, `OR`, and `NOT`
evaluation retains both the outcome and a structural trace.

## Safety and conflict handling

Risk escalation is ordinal and monotonic: the highest matched rank prevails regardless of rule
priority. Recommendations are restricted to that tier so routine guidance cannot compete with
emergency instructions. Priority gives deterministic ordering within a tier. No-match behavior
remains neutral and does not claim that an eye is healthy.

The match score is calculated from satisfied authored criteria. It is isolated from risk
resolution and explicitly described as neither diagnostic probability nor clinical confidence.

## Evaluation

Tests cover all eight comparisons, nested expressions, truth tables, strict types, missing
facts, exclusions, deterministic ordering, risk conflicts, recommendation suppression,
no-match behavior, deduplication, scores, stable traces, concurrency, CLI behavior, all 21
authored rules, and an added JSON rule without engine modification.

## Limitations

The engine demonstrates deterministic implementation, not diagnostic accuracy or clinical
validity. Rules currently conclude outcomes and do not assert derived facts, so forward
chaining reaches its fixed point in one pass. Consultation APIs and presentation remain later
phase work.
