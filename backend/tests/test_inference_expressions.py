import pytest

from app.inference import InferenceConfigurationError, TruthValue, evaluate_expression


def _predicate(fact_id):
    return {"fact_id": fact_id, "operator": "eq", "value": True}


@pytest.mark.parametrize(
    ("operator", "actual", "expected", "truth"),
    [
        ("eq", True, True, TruthValue.TRUE),
        ("neq", "gradual", "sudden", TruthValue.TRUE),
        ("in", "gradual", ["sudden", "gradual"], TruthValue.TRUE),
        ("not_in", "uncertain", ["sudden", "gradual"], TruthValue.TRUE),
        ("gt", 61, 60, TruthValue.TRUE),
        ("gte", 60, 60, TruthValue.TRUE),
        ("lt", 59, 60, TruthValue.TRUE),
        ("lte", 60, 60, TruthValue.TRUE),
    ],
)
def test_all_supported_comparison_operators(operator, actual, expected, truth):
    result = evaluate_expression(
        {"fact_id": "fact_test", "operator": operator, "value": expected},
        {"fact_test": actual},
    )

    assert result.truth is truth
    assert result.score.to_dict() == {
        "total": 1,
        "known": 1,
        "satisfied": 1,
        "percentage": 100.0,
    }


@pytest.mark.parametrize(
    ("expression", "facts", "expected"),
    [
        ({"all": [_predicate("a"), _predicate("b")]}, {"a": True, "b": True}, "true"),
        ({"all": [_predicate("a"), _predicate("b")]}, {"a": False}, "false"),
        ({"all": [_predicate("a"), _predicate("b")]}, {"a": True}, "unknown"),
        ({"any": [_predicate("a"), _predicate("b")]}, {"a": True}, "true"),
        ({"any": [_predicate("a"), _predicate("b")]}, {"a": False, "b": False}, "false"),
        ({"any": [_predicate("a"), _predicate("b")]}, {"a": False}, "unknown"),
        ({"not": _predicate("a")}, {"a": False}, "true"),
        ({"not": _predicate("a")}, {}, "unknown"),
    ],
)
def test_strong_kleene_truth_tables(expression, facts, expected):
    result = evaluate_expression(expression, facts)

    assert result.truth.value == expected


def test_nested_not_uses_effective_criterion_polarity():
    result = evaluate_expression(
        {"not": {"any": [_predicate("a"), _predicate("b")]}},
        {"a": False, "b": False},
    )

    assert result.truth is TruthValue.TRUE
    assert result.score.satisfied == 2
    assert result.score.percentage == 100.0


def test_missing_fact_is_visible_and_never_satisfies_not():
    result = evaluate_expression({"not": _predicate("a")}, {})
    payload = result.trace.to_dict()

    assert result.truth is TruthValue.UNKNOWN
    assert result.missing_fact_ids == ("a",)
    assert payload["children"][0]["missing"] is True
    assert "actual" not in payload["children"][0]


@pytest.mark.parametrize(
    "expression",
    [
        {"fact_id": "a", "operator": "in", "value": "not-an-array"},
        {"fact_id": "a", "operator": "gt", "value": 2},
        {"fact_id": "a", "operator": "unsupported", "value": True},
        {"unexpected": []},
    ],
)
def test_invalid_authored_expression_fails_closed(expression):
    facts = {"a": "value"} if expression.get("operator") != "gt" else {"a": True}

    with pytest.raises(InferenceConfigurationError):
        evaluate_expression(expression, facts)


def test_bool_and_integer_are_not_equal():
    result = evaluate_expression({"fact_id": "a", "operator": "eq", "value": 1}, {"a": True})

    assert result.truth is TruthValue.FALSE
