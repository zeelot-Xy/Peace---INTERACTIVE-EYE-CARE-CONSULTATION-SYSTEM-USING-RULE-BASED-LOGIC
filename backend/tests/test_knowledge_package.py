from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from jsonschema import Draft202012Validator

from tools.validate_knowledge_package import DEFAULT_PACKAGE, DEFAULT_SCHEMAS, validate_package


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rewrite_json(path: Path, document) -> None:
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _refresh_manifest_checksum(package: Path, filename: str) -> None:
    manifest_path = package / "manifest.json"
    manifest = _read(manifest_path)
    data = (package / filename).read_bytes().replace(b"\r\n", b"\n")
    digest = hashlib.sha256(data).hexdigest()
    next(entry for entry in manifest["files"] if entry["name"] == filename)["sha256"] = digest
    _rewrite_json(manifest_path, manifest)


def test_every_schema_is_valid_draft_2020_12():
    for schema_path in DEFAULT_SCHEMAS.glob("*.schema.json"):
        Draft202012Validator.check_schema(_read(schema_path))


def test_first_knowledge_package_passes_all_authoring_checks():
    assert validate_package() == []


def test_package_has_approved_scope_and_minimum_content():
    manifest = _read(DEFAULT_PACKAGE / "manifest.json")
    assert manifest["scope"]["minimum_age"] == 18
    assert manifest["language"] == "en"
    assert "not a diagnosis" in manifest["disclaimer"].lower()
    assert len(_read(DEFAULT_PACKAGE / "conditions.json")["conditions"]) >= 14
    assert len(_read(DEFAULT_PACKAGE / "symptoms.json")["symptoms"]) >= 30
    assert len(_read(DEFAULT_PACKAGE / "questions.json")["questions"]) >= 25
    assert len(_read(DEFAULT_PACKAGE / "rules.json")["rules"]) >= 16


def test_each_assertion_collection_has_citations():
    collections = {
        "conditions.json": "conditions",
        "questions.json": "questions",
        "recommendations.json": "recommendations",
        "risk-levels.json": "risk_levels",
        "rules.json": "rules",
        "symptoms.json": "symptoms",
    }
    for filename, collection in collections.items():
        for item in _read(DEFAULT_PACKAGE / filename)[collection]:
            assert item["citation_ids"], f"{filename}:{item['id']} has no citations"


def test_emergency_rules_have_priority_and_multiple_sources():
    rules = _read(DEFAULT_PACKAGE / "rules.json")["rules"]
    emergency_rules = [rule for rule in rules if rule["risk_id"] == "risk_emergency"]
    assert emergency_rules
    for rule in emergency_rules:
        assert rule["priority"] >= 900
        assert len(rule["citation_ids"]) >= 2


def test_checksum_tampering_is_reported(tmp_path: Path):
    package = tmp_path / "package"
    shutil.copytree(DEFAULT_PACKAGE, package)
    with (package / "conditions.json").open("a", encoding="utf-8") as handle:
        handle.write(" ")

    issues = validate_package(package)

    assert any(issue.code == "checksum_mismatch" for issue in issues)


def test_broken_reference_is_reported(tmp_path: Path):
    package = tmp_path / "package"
    shutil.copytree(DEFAULT_PACKAGE, package)
    rules_path = package / "rules.json"
    rules = _read(rules_path)
    rules["rules"][0]["recommendation_ids"] = ["recommendation_missing"]
    _rewrite_json(rules_path, rules)
    _refresh_manifest_checksum(package, "rules.json")

    issues = validate_package(package)

    assert any(
        issue.code == "broken_reference" and "recommendation_missing" in issue.message
        for issue in issues
    )


def test_prohibited_diagnostic_wording_is_reported(tmp_path: Path):
    package = tmp_path / "package"
    shutil.copytree(DEFAULT_PACKAGE, package)
    conditions_path = package / "conditions.json"
    conditions = _read(conditions_path)
    conditions["conditions"][0]["summary"] = (
        "You have a refractive error based on this questionnaire result."
    )
    _rewrite_json(conditions_path, conditions)
    _refresh_manifest_checksum(package, "conditions.json")

    issues = validate_package(package)

    assert any(issue.code == "prohibited_wording" for issue in issues)


def test_risk_order_is_fixed_for_safety(tmp_path: Path):
    package = tmp_path / "package"
    shutil.copytree(DEFAULT_PACKAGE, package)
    risk_path = package / "risk-levels.json"
    risks = _read(risk_path)
    risks["risk_levels"][0]["rank"] = 2
    _rewrite_json(risk_path, risks)
    _refresh_manifest_checksum(package, "risk-levels.json")

    issues = validate_package(package)

    assert any(issue.code == "invalid_risk_order" for issue in issues)
