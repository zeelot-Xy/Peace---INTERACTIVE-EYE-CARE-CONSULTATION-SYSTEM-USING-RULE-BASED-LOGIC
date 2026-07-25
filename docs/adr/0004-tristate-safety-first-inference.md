# ADR 0004: Tri-State Safety-First Inference

- Status: Accepted
- Date: 2026-07-23

## Context

Consultations are progressively answered, so treating an absent response as false could
incorrectly satisfy an exclusion or suppress a safety rule. Several rules may also match at
different urgency levels. Results must be reproducible and explainable without presenting a
heuristic score as diagnostic probability.

## Decision

Use a stateless forward-chaining engine over one immutable knowledge snapshot. Evaluate nested
expressions with strong-Kleene `TRUE`, `FALSE`, and `UNKNOWN` semantics. Only true rules fire;
unknown rules remain pending. Order evaluation deterministically by priority and stable ID.

Resolve conflicts by authored risk rank. Emit recommendations only from the highest matched
tier while preserving all matched indications and traces. Calculate a rule-coverage score from
authored leaf criteria, label it as non-probabilistic, and exclude it from safety decisions.
Retain a complete trace without timestamps, random IDs, automatic patient-fact logging, or
inferred medical text.

## Consequences

- Missing facts cannot silently become negative evidence.
- Confirmed red flags can escalate during an incomplete consultation.
- Repeated and concurrent evaluations are stable without shared mutable state.
- Lower-risk matches remain explainable but cannot dilute urgent instructions.
- Current output-only rules reach a fixed point in one pass.
- Technical transparency does not provide clinical validation.
