import json


def test_inference_cli_emits_machine_readable_result(app, tmp_path):
    facts_file = tmp_path / "demo-facts.json"
    facts_file.write_text(json.dumps({"fact_chemical_exposure": True}), encoding="utf-8")

    result = app.test_cli_runner().invoke(
        args=["inference-evaluate", "--facts-file", str(facts_file), "--json"]
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["overall_risk"]["id"] == "risk_emergency"
    assert payload["matched_rules"][0]["rule_id"] == "rule_chemical_exposure"


def test_inference_cli_rejects_invalid_fact_with_nonzero_exit(app, tmp_path):
    facts_file = tmp_path / "bad-facts.json"
    facts_file.write_text(json.dumps({"fact_unknown": True}), encoding="utf-8")

    result = app.test_cli_runner().invoke(
        args=["inference-evaluate", "--facts-file", str(facts_file), "--json"]
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["code"] == "invalid_facts"


def test_inference_cli_rejects_malformed_json(app, tmp_path):
    facts_file = tmp_path / "bad.json"
    facts_file.write_text("{", encoding="utf-8")

    result = app.test_cli_runner().invoke(
        args=["inference-evaluate", "--facts-file", str(facts_file)]
    )

    assert result.exit_code == 1
    assert "Unable to read facts JSON" in result.output
