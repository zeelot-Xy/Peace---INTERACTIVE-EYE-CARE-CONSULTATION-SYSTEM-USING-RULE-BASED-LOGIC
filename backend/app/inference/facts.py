"""Strict normalization of facts against the active knowledge snapshot."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from app.inference.exceptions import FactValidationError, FactValidationIssue
from app.knowledge import KnowledgePackage


def _same_value(left: Any, right: Any) -> bool:
    return type(left) is type(right) and left == right


def normalize_facts(package: KnowledgePackage, supplied: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate and copy facts without mutating caller-owned input."""

    if not isinstance(supplied, Mapping):
        raise FactValidationError(
            (FactValidationIssue("invalid_container", "$", "Facts must be supplied as an object."),)
        )
    issues: list[FactValidationIssue] = []
    normalized: dict[str, Any] = {}
    definitions = package.indexes["symptoms"]
    for fact_id in sorted(supplied, key=str):
        if not isinstance(fact_id, str):
            issues.append(
                FactValidationIssue(
                    "invalid_fact_id", str(fact_id), "Fact identifiers must be strings."
                )
            )
            continue
        value = supplied[fact_id]
        definition = definitions.get(fact_id)
        if definition is None:
            issues.append(FactValidationIssue("unknown_fact", fact_id, "Fact is not defined."))
            continue
        if value is None:
            issues.append(
                FactValidationIssue(
                    "null_value", fact_id, "Omit an unanswered fact instead of using null."
                )
            )
            continue
        value_type = definition["value_type"]
        if value_type == "boolean" and type(value) is not bool:
            issues.append(FactValidationIssue("invalid_type", fact_id, "Expected a boolean value."))
            continue
        if value_type == "integer":
            if type(value) is not int:
                issues.append(
                    FactValidationIssue("invalid_type", fact_id, "Expected an integer value.")
                )
                continue
            if value < definition["minimum"] or value > definition["maximum"]:
                issues.append(
                    FactValidationIssue(
                        "out_of_range",
                        fact_id,
                        f"Value must be between {definition['minimum']} and "
                        f"{definition['maximum']}.",
                    )
                )
                continue
        if value_type == "choice" and not any(
            _same_value(value, allowed) for allowed in definition["allowed_values"]
        ):
            issues.append(
                FactValidationIssue("invalid_choice", fact_id, "Value is not an allowed choice.")
            )
            continue
        normalized[fact_id] = value
    if issues:
        raise FactValidationError(tuple(issues))
    return MappingProxyType(normalized)
