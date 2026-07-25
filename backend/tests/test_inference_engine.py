import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from types import MappingProxyType

import pytest

from app.inference import MATCH_SCORE_NOTICE, InferenceEngine
from app.knowledge.contracts import freeze


@pytest.fixture()
def knowledge_package(app):
    return app.extensions["knowledge"].get_active()


@pytest.fixture()
def engine(app):
    return app.extensions["inference"]


def _complete_negative_facts(package):
    facts = {}
    for definition in package.collections["symptoms"]:
        if definition["value_type"] == "boolean":
            facts[definition["id"]] = False
        elif definition["value_type"] == "integer":
            facts[definition["id"]] = definition["minimum"]
        else:
            facts[definition["id"]] = definition["allowed_values"][0]
    return facts


def _satisfy(expression, facts, package, negate=False):
    if "fact_id" in expression:
        fact_id = expression["fact_id"]
        operator = expression["operator"]
        expected = expression["value"]
        definition = package.indexes["symptoms"][fact_id]
        should_match = not negate
        if operator == "eq":
            if should_match:
                facts[fact_id] = expected
            elif definition["value_type"] == "boolean":
                facts[fact_id] = not expected
            elif definition["value_type"] == "integer":
                facts[fact_id] = expected + 1
            else:
                facts[fact_id] = next(
                    value for value in definition["allowed_values"] if value != expected
                )
        elif operator == "neq":
            _satisfy(
                {"fact_id": fact_id, "operator": "eq", "value": expected},
                facts,
                package,
                should_match,
            )
        elif operator in {"gte", "gt"}:
            facts[fact_id] = expected + (operator == "gt") if should_match else expected - 1
        elif operator in {"lte", "lt"}:
            facts[fact_id] = expected - (operator == "lt") if should_match else expected + 1
        else:
            choices = tuple(expected)
            if should_match == (operator == "in"):
                facts[fact_id] = choices[0]
            else:
                facts[fact_id] = next(
                    value for value in definition["allowed_values"] if value not in choices
                )
        return
    if "not" in expression:
        _satisfy(expression["not"], facts, package, not negate)
        return
    kind = "all" if "all" in expression else "any"
    children = expression[kind]
    effective_all = (kind == "all") != negate
    selected = children if effective_all else children[:1]
    for child in selected:
        _satisfy(child, facts, package, negate)


def test_partial_emergency_match_is_not_blocked_by_unrelated_missing_facts(
    engine, knowledge_package
):
    result = engine.evaluate(knowledge_package, {"fact_chemical_exposure": True})

    assert result.outcome_state == "matched"
    assert result.completeness_state == "incomplete"
    assert result.overall_risk["id"] == "risk_emergency"
    assert result.matched_rules[0].rule_id == "rule_chemical_exposure"
    assert result.red_flags


def test_highest_safety_risk_wins_and_lower_tier_advice_is_suppressed(engine, knowledge_package):
    facts = {
        "fact_chemical_exposure": True,
        "fact_diabetes": True,
        "fact_painless_eyelid_lump": True,
    }

    result = engine.evaluate(knowledge_package, facts)

    assert result.overall_risk["rank"] == 4
    assert {item["id"] for item in result.recommendations} == {"recommendation_chemical_first_aid"}
    assert "condition_diabetic_retinopathy_risk" in {
        item["id"] for item in result.possible_indications
    }


def test_same_tier_outputs_are_deduplicated_with_stable_support(engine, knowledge_package):
    result = engine.evaluate(
        knowledge_package,
        {"fact_chemical_exposure": True, "fact_high_speed_impact": True},
    )

    injury = next(
        item for item in result.possible_indications if item["id"] == "condition_eye_injury_pattern"
    )
    assert injury["supporting_rule_ids"] == (
        "rule_chemical_exposure",
        "rule_high_speed_impact",
    )
    with pytest.raises(TypeError):
        injury["name"] = "changed"
    assert len({source["id"] for source in result.evidence}) == len(result.evidence)


def test_no_match_is_neutral_and_does_not_invent_reassurance(engine, knowledge_package):
    result = engine.evaluate(knowledge_package, _complete_negative_facts(knowledge_package))

    assert result.outcome_state == "no_match"
    assert result.completeness_state == "complete"
    assert result.overall_risk is None
    assert result.recommendations == ()
    assert result.possible_indications == ()
    assert result.evidence == ()


def test_empty_facts_are_pending_not_false(engine, knowledge_package):
    result = engine.evaluate(knowledge_package, {})

    assert result.outcome_state == "no_match"
    assert result.completeness_state == "incomplete"
    assert len(result.pending_rules) == len(knowledge_package.collections["rules"])
    assert result.missing_fact_ids


def test_score_wording_and_calculation_are_non_diagnostic(engine, knowledge_package):
    result = engine.evaluate(
        knowledge_package,
        {"fact_burning": True, "fact_watering": True},
    )
    dry_eye = next(rule for rule in result.matched_rules if rule.rule_id == "rule_dry_eye")

    assert dry_eye.score.total == 4
    assert dry_eye.score.satisfied == 2
    assert dry_eye.score.percentage == 50.0
    assert result.match_score_notice == MATCH_SCORE_NOTICE
    assert "probability" in MATCH_SCORE_NOTICE


def test_result_and_trace_are_repeatable_json(engine, knowledge_package):
    facts = {"fact_age_years": 64, "fact_central_distortion": True}

    first = json.dumps(engine.evaluate(knowledge_package, facts).to_dict(), sort_keys=True)
    second = json.dumps(engine.evaluate(knowledge_package, facts).to_dict(), sort_keys=True)

    assert first == second
    assert knowledge_package.fingerprint in first
    assert "timestamp" not in first


def test_engine_is_stateless_under_concurrent_evaluation(engine, knowledge_package):
    cases = [
        {"fact_chemical_exposure": True},
        {"fact_diabetes": True},
        {"fact_painless_eyelid_lump": True},
        {},
    ]

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda facts: engine.evaluate(knowledge_package, facts), cases))

    assert [result.outcome_state for result in results] == [
        "matched",
        "matched",
        "matched",
        "no_match",
    ]


def test_every_authored_rule_has_a_matching_scenario(engine, knowledge_package):
    for rule in knowledge_package.collections["rules"]:
        facts = _complete_negative_facts(knowledge_package)
        _satisfy(rule["when"], facts, knowledge_package)

        result = engine.evaluate(knowledge_package, facts)

        assert rule["id"] in {item.rule_id for item in result.matched_rules}


def test_new_json_rule_executes_without_engine_code_change(engine, knowledge_package):
    new_rule = freeze(
        {
            "id": "rule_runtime_extension",
            "name": "Runtime extension proof",
            "priority": 410,
            "when": {
                "fact_id": "fact_screen_related",
                "operator": "eq",
                "value": True,
            },
            "conclusion_ids": ["condition_dry_eye"],
            "risk_id": "risk_routine",
            "recommendation_ids": ["recommendation_routine_exam"],
            "rationale": "A test-only extension demonstrates data-driven rule execution.",
            "explanation_template": "The test-only authored criterion was satisfied.",
            "citation_ids": ["source_nei_dry_eye"],
        }
    )
    collections = dict(knowledge_package.collections)
    collections["rules"] = (*collections["rules"], new_rule)
    extended = replace(
        knowledge_package,
        collections=MappingProxyType(collections),
        fingerprint="test-extension-fingerprint",
    )

    result = engine.evaluate(extended, {"fact_screen_related": True})

    assert "rule_runtime_extension" in {rule.rule_id for rule in result.matched_rules}
    assert isinstance(engine, InferenceEngine)
