"""Recursive three-valued evaluation of authored rule expressions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.inference.contracts import (
    CriteriaScore,
    ExpressionEvaluation,
    ExpressionTrace,
    TruthValue,
)
from app.inference.exceptions import InferenceConfigurationError


def _same_value(left: Any, right: Any) -> bool:
    return type(left) is type(right) and left == right


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "eq":
        return _same_value(actual, expected)
    if operator == "neq":
        return not _same_value(actual, expected)
    if operator in {"in", "not_in"}:
        if not isinstance(expected, (list, tuple)):
            raise InferenceConfigurationError(f"Operator '{operator}' requires an array.")
        contained = any(_same_value(actual, item) for item in expected)
        return contained if operator == "in" else not contained
    if operator in {"gt", "gte", "lt", "lte"}:
        if type(actual) is not int or type(expected) is not int:
            raise InferenceConfigurationError(f"Operator '{operator}' requires integers.")
        return {
            "gt": actual > expected,
            "gte": actual >= expected,
            "lt": actual < expected,
            "lte": actual <= expected,
        }[operator]
    raise InferenceConfigurationError(f"Unsupported rule operator: {operator!r}.")


def _combine(kind: str, values: tuple[TruthValue, ...]) -> TruthValue:
    if kind == "all":
        if TruthValue.FALSE in values:
            return TruthValue.FALSE
        return (
            TruthValue.TRUE
            if all(value is TruthValue.TRUE for value in values)
            else TruthValue.UNKNOWN
        )
    if TruthValue.TRUE in values:
        return TruthValue.TRUE
    return (
        TruthValue.FALSE
        if all(value is TruthValue.FALSE for value in values)
        else TruthValue.UNKNOWN
    )


def evaluate_expression(
    expression: Mapping[str, Any], facts: Mapping[str, Any], path: str = "$"
) -> ExpressionEvaluation:
    """Evaluate an expression with strong-Kleene missing-fact semantics."""

    return _evaluate(expression, facts, path, negated=False)


def _evaluate(
    expression: Mapping[str, Any],
    facts: Mapping[str, Any],
    path: str,
    *,
    negated: bool,
) -> ExpressionEvaluation:
    if "fact_id" in expression:
        fact_id = str(expression["fact_id"])
        missing = fact_id not in facts
        base = (
            TruthValue.UNKNOWN
            if missing
            else (
                TruthValue.TRUE
                if _compare(facts[fact_id], str(expression["operator"]), expression["value"])
                else TruthValue.FALSE
            )
        )
        truth = base.negate() if negated else base
        trace = ExpressionTrace(
            path=path,
            kind="predicate",
            truth=truth,
            fact_id=fact_id,
            operator=str(expression["operator"]),
            expected=expression["value"],
            actual=None if missing else facts[fact_id],
            missing=missing,
        )
        return ExpressionEvaluation(
            truth,
            trace,
            CriteriaScore(1, 0 if missing else 1, 1 if truth is TruthValue.TRUE else 0),
            (fact_id,) if missing else (),
        )

    if "not" in expression:
        child = _evaluate(expression["not"], facts, f"{path}.not", negated=not negated)
        trace = ExpressionTrace(path, "not", child.truth, (child.trace,))
        return ExpressionEvaluation(child.truth, trace, child.score, child.missing_fact_ids)

    authored_kind = "all" if "all" in expression else "any" if "any" in expression else None
    if authored_kind is None:
        raise InferenceConfigurationError(f"Malformed expression at {path}.")
    effective_kind = ("any" if authored_kind == "all" else "all") if negated else authored_kind
    children = tuple(
        _evaluate(child, facts, f"{path}.{authored_kind}[{index}]", negated=negated)
        for index, child in enumerate(expression[authored_kind])
    )
    truth = _combine(effective_kind, tuple(child.truth for child in children))
    score = CriteriaScore(
        sum(child.score.total for child in children),
        sum(child.score.known for child in children),
        sum(child.score.satisfied for child in children),
    )
    missing = tuple(sorted({fact_id for child in children for fact_id in child.missing_fact_ids}))
    trace = ExpressionTrace(path, authored_kind, truth, tuple(child.trace for child in children))
    return ExpressionEvaluation(truth, trace, score, missing)
