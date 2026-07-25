"""Deterministic, stateless rule evaluation and safety aggregation."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from app.inference.contracts import InferenceResult, RuleEvaluation, TruthValue
from app.inference.expressions import evaluate_expression
from app.inference.facts import normalize_facts
from app.knowledge import KnowledgePackage

MATCH_SCORE_NOTICE = (
    "The rule-match score is the percentage of authored criteria satisfied by the "
    "provided facts. It is not a diagnostic probability or clinical confidence score."
)


def _public_item(item: Mapping[str, Any], *, exclude: tuple[str, ...] = ()) -> Mapping[str, Any]:
    return MappingProxyType({key: value for key, value in item.items() if key not in exclude})


class InferenceEngine:
    """Evaluate one immutable knowledge snapshot without retaining patient facts."""

    def evaluate(
        self, package: KnowledgePackage, supplied_facts: Mapping[str, Any]
    ) -> InferenceResult:
        facts = normalize_facts(package, supplied_facts)
        risk_index = package.indexes["risk_levels"]
        evaluations = tuple(
            self._evaluate_rule(rule, facts)
            for rule in sorted(
                package.collections["rules"], key=lambda item: (-item["priority"], item["id"])
            )
        )
        matched = tuple(
            sorted(
                (rule for rule in evaluations if rule.status == "matched"),
                key=lambda item: (
                    -risk_index[item.risk_id]["rank"],
                    -item.priority,
                    item.rule_id,
                ),
            )
        )
        pending = tuple(rule for rule in evaluations if rule.status == "pending")
        overall = (
            max(
                (risk_index[rule.risk_id] for rule in matched),
                key=lambda item: (item["rank"], item["id"]),
            )
            if matched
            else None
        )
        highest_rank = overall["rank"] if overall else None
        highest_rules = tuple(
            rule for rule in matched if risk_index[rule.risk_id]["rank"] == highest_rank
        )
        indications = self._indications(package, matched)
        recommendations = self._referenced_items(
            package.indexes["recommendations"],
            (item_id for rule in highest_rules for item_id in rule.recommendation_ids),
        )
        red_flags = tuple(
            MappingProxyType(
                {
                    "rule_id": rule.rule_id,
                    "risk_id": rule.risk_id,
                    "risk_label": risk_index[rule.risk_id]["label"],
                    "explanation": rule.explanation,
                }
            )
            for rule in matched
            if risk_index[rule.risk_id]["rank"] >= 3
        )
        evidence_ids = {
            source_id
            for rule in matched
            for source_id in (
                *rule.citation_ids,
                *risk_index[rule.risk_id]["citation_ids"],
            )
        }
        for item in (*indications, *recommendations):
            evidence_ids.update(item["citation_ids"])
        evidence = tuple(
            _public_item(package.indexes["sources"][source_id])
            for source_id in sorted(evidence_ids)
        )
        missing = tuple(sorted({fact_id for rule in pending for fact_id in rule.missing_fact_ids}))
        return InferenceResult(
            outcome_state="matched" if matched else "no_match",
            completeness_state="incomplete" if pending else "complete",
            package_id=package.package_id,
            knowledge_version=package.content_version,
            knowledge_fingerprint=package.fingerprint,
            overall_risk=_public_item(overall) if overall else None,
            matched_rules=matched,
            pending_rules=pending,
            possible_indications=indications,
            recommendations=recommendations,
            red_flags=red_flags,
            missing_fact_ids=missing,
            evidence=evidence,
            inference_trace=evaluations,
            disclaimer=str(package.manifest["disclaimer"]),
            match_score_notice=MATCH_SCORE_NOTICE,
        )

    @staticmethod
    def _evaluate_rule(rule: Mapping[str, Any], facts: Mapping[str, Any]) -> RuleEvaluation:
        expression = evaluate_expression(rule["when"], facts)
        status = {
            TruthValue.TRUE: "matched",
            TruthValue.FALSE: "unmatched",
            TruthValue.UNKNOWN: "pending",
        }[expression.truth]
        return RuleEvaluation(
            rule_id=str(rule["id"]),
            name=str(rule["name"]),
            priority=int(rule["priority"]),
            status=status,
            truth=expression.truth,
            score=expression.score,
            missing_fact_ids=expression.missing_fact_ids,
            conclusion_ids=tuple(rule["conclusion_ids"]),
            risk_id=str(rule["risk_id"]),
            recommendation_ids=tuple(rule["recommendation_ids"]),
            rationale=str(rule["rationale"]),
            explanation=str(rule["explanation_template"]),
            citation_ids=tuple(rule["citation_ids"]),
            trace=expression.trace,
        )

    @staticmethod
    def _referenced_items(
        index: Mapping[str, Mapping[str, Any]], identifiers: Any
    ) -> tuple[Mapping[str, Any], ...]:
        return tuple(_public_item(index[item_id]) for item_id in sorted(set(identifiers)))

    @staticmethod
    def _indications(
        package: KnowledgePackage, matched: tuple[RuleEvaluation, ...]
    ) -> tuple[Mapping[str, Any], ...]:
        supporting: dict[str, list[str]] = {}
        for rule in matched:
            for condition_id in rule.conclusion_ids:
                supporting.setdefault(condition_id, []).append(rule.rule_id)
        results = []
        for condition_id in sorted(supporting):
            condition = dict(package.indexes["conditions"][condition_id])
            condition["supporting_rule_ids"] = tuple(supporting[condition_id])
            results.append(MappingProxyType(condition))
        return tuple(results)
