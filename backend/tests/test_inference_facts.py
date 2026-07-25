from copy import deepcopy

import pytest

from app.inference import FactValidationError, normalize_facts


@pytest.fixture()
def knowledge_package(app):
    return app.extensions["knowledge"].get_active()


def test_valid_facts_are_copied_and_input_is_not_mutated(knowledge_package):
    supplied = {
        "fact_age_years": 42,
        "fact_redness": True,
        "fact_symptom_onset": "gradual",
    }
    before = deepcopy(supplied)

    normalized = normalize_facts(knowledge_package, supplied)

    assert dict(normalized) == supplied
    assert supplied == before
    with pytest.raises(TypeError):
        normalized["fact_redness"] = False


@pytest.mark.parametrize(
    ("facts", "code"),
    [
        ({"fact_not_defined": True}, "unknown_fact"),
        ({"fact_redness": None}, "null_value"),
        ({"fact_redness": 1}, "invalid_type"),
        ({"fact_age_years": True}, "invalid_type"),
        ({"fact_age_years": 17}, "out_of_range"),
        ({"fact_age_years": 121}, "out_of_range"),
        ({"fact_symptom_onset": "later"}, "invalid_choice"),
    ],
)
def test_invalid_facts_return_stable_field_errors(knowledge_package, facts, code):
    with pytest.raises(FactValidationError) as captured:
        normalize_facts(knowledge_package, facts)

    assert captured.value.issues[0].code == code
    assert "password" not in str(captured.value.to_dict()).lower()


def test_integer_boundaries_are_accepted(knowledge_package):
    normalized = normalize_facts(knowledge_package, {"fact_age_years": 18, "fact_redness": False})

    assert normalized["fact_age_years"] == 18


def test_non_mapping_facts_are_rejected(knowledge_package):
    with pytest.raises(FactValidationError) as captured:
        normalize_facts(knowledge_package, [])

    assert captured.value.issues[0].code == "invalid_container"
