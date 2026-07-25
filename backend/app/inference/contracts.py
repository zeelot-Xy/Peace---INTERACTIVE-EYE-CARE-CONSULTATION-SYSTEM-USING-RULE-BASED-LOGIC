"""Immutable, JSON-serializable inference contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class TruthValue(StrEnum):
    """Three-valued truth used when consultation facts are incomplete."""

    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"

    def negate(self) -> TruthValue:
        if self is TruthValue.TRUE:
            return TruthValue.FALSE
        if self is TruthValue.FALSE:
            return TruthValue.TRUE
        return TruthValue.UNKNOWN


@dataclass(frozen=True)
class CriteriaScore:
    total: int
    known: int
    satisfied: int

    @property
    def percentage(self) -> float:
        return round((self.satisfied / self.total) * 100, 2) if self.total else 0.0

    def to_dict(self) -> dict[str, int | float]:
        return {
            "total": self.total,
            "known": self.known,
            "satisfied": self.satisfied,
            "percentage": self.percentage,
        }


@dataclass(frozen=True)
class ExpressionTrace:
    path: str
    kind: str
    truth: TruthValue
    children: tuple[ExpressionTrace, ...] = ()
    fact_id: str | None = None
    operator: str | None = None
    expected: Any = None
    actual: Any = None
    missing: bool = False

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "path": self.path,
            "kind": self.kind,
            "truth": self.truth.value,
        }
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        if self.fact_id is not None:
            result.update(
                {
                    "fact_id": self.fact_id,
                    "operator": self.operator,
                    "expected": self.expected,
                    "missing": self.missing,
                }
            )
            if not self.missing:
                result["actual"] = self.actual
        return result


@dataclass(frozen=True)
class ExpressionEvaluation:
    truth: TruthValue
    trace: ExpressionTrace
    score: CriteriaScore
    missing_fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class RuleEvaluation:
    rule_id: str
    name: str
    priority: int
    status: str
    truth: TruthValue
    score: CriteriaScore
    missing_fact_ids: tuple[str, ...]
    conclusion_ids: tuple[str, ...]
    risk_id: str
    recommendation_ids: tuple[str, ...]
    rationale: str
    explanation: str
    citation_ids: tuple[str, ...]
    trace: ExpressionTrace

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "priority": self.priority,
            "status": self.status,
            "truth": self.truth.value,
            "match_score": self.score.to_dict(),
            "missing_fact_ids": list(self.missing_fact_ids),
            "conclusion_ids": list(self.conclusion_ids),
            "risk_id": self.risk_id,
            "recommendation_ids": list(self.recommendation_ids),
            "rationale": self.rationale,
            "explanation": self.explanation,
            "citation_ids": list(self.citation_ids),
            "expression": self.trace.to_dict(),
        }


@dataclass(frozen=True)
class InferenceResult:
    outcome_state: str
    completeness_state: str
    package_id: str
    knowledge_version: str
    knowledge_fingerprint: str
    overall_risk: Mapping[str, Any] | None
    matched_rules: tuple[RuleEvaluation, ...]
    pending_rules: tuple[RuleEvaluation, ...]
    possible_indications: tuple[Mapping[str, Any], ...]
    recommendations: tuple[Mapping[str, Any], ...]
    red_flags: tuple[Mapping[str, Any], ...]
    missing_fact_ids: tuple[str, ...]
    evidence: tuple[Mapping[str, Any], ...]
    inference_trace: tuple[RuleEvaluation, ...]
    disclaimer: str
    match_score_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome_state": self.outcome_state,
            "completeness_state": self.completeness_state,
            "knowledge": {
                "package_id": self.package_id,
                "content_version": self.knowledge_version,
                "fingerprint": self.knowledge_fingerprint,
            },
            "overall_risk": _to_json(self.overall_risk),
            "matched_rules": [rule.to_dict() for rule in self.matched_rules],
            "pending_rules": [rule.to_dict() for rule in self.pending_rules],
            "possible_indications": _to_json(self.possible_indications),
            "recommendations": _to_json(self.recommendations),
            "red_flags": _to_json(self.red_flags),
            "missing_fact_ids": list(self.missing_fact_ids),
            "evidence": _to_json(self.evidence),
            "inference_trace": [rule.to_dict() for rule in self.inference_trace],
            "disclaimer": self.disclaimer,
            "match_score_notice": self.match_score_notice,
        }


def _to_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _to_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_json(item) for item in value]
    return value
