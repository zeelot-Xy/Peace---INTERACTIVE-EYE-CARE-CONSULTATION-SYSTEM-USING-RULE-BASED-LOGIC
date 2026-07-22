from __future__ import annotations

import hashlib
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import MappingProxyType

import pytest

from app import create_app
from app.knowledge import KnowledgeLoadError, KnowledgeManager
from app.knowledge.validation import validate_package
from tools.validate_knowledge_package import DEFAULT_PACKAGE, DEFAULT_SCHEMAS


def _copy_package(tmp_path: Path, name: str = "candidate") -> Path:
    package = tmp_path / name
    shutil.copytree(DEFAULT_PACKAGE, package)
    return package


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, document) -> None:
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def _refresh_checksum(package: Path, filename: str) -> None:
    manifest_path = package / "manifest.json"
    manifest = _read(manifest_path)
    data = (package / filename).read_bytes().replace(b"\r\n", b"\n")
    digest = hashlib.sha256(data).hexdigest()
    next(item for item in manifest["files"] if item["name"] == filename)["sha256"] = digest
    _write(manifest_path, manifest)


def test_valid_package_loads_as_immutable_indexed_snapshot():
    manager = KnowledgeManager(DEFAULT_SCHEMAS)

    report = manager.activate(DEFAULT_PACKAGE)
    package = manager.get_active()

    assert report.valid
    assert package.package_id == "eye-care-en-1.0.0"
    assert isinstance(package.manifest, MappingProxyType)
    assert package.indexes["rules"]["rule_sudden_vision_loss"]["priority"] >= 900
    with pytest.raises(TypeError):
        package.manifest["status"] = "published"
    with pytest.raises(TypeError):
        package.indexes["rules"]["rule_sudden_vision_loss"]["priority"] = 1


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        (lambda package: (package / "manifest.json").unlink(), "missing_file"),
        (lambda package: (package / "rules.json").unlink(), "missing_file"),
        (
            lambda package: (package / "rules.json").write_text("{", encoding="utf-8"),
            "malformed_json",
        ),
    ],
)
def test_missing_and_malformed_files_are_reported(tmp_path: Path, mutation, expected_code: str):
    package = _copy_package(tmp_path)
    mutation(package)

    report = validate_package(package, DEFAULT_SCHEMAS)

    assert not report.valid
    assert expected_code in {issue.code for issue in report.issues}


def test_schema_invalid_manifest_shape_returns_report_instead_of_crashing(tmp_path: Path):
    package = _copy_package(tmp_path)
    (package / "manifest.json").write_text("[]", encoding="utf-8")

    report = validate_package(package, DEFAULT_SCHEMAS)

    assert not report.valid
    assert "schema_validation" in {issue.code for issue in report.issues}


def test_schema_error_duplicate_id_and_broken_reference_are_reported(tmp_path: Path):
    package = _copy_package(tmp_path)
    rules_path = package / "rules.json"
    rules = _read(rules_path)
    rules["rules"][0]["id"] = rules["rules"][1]["id"]
    rules["rules"][0]["recommendation_ids"] = ["recommendation_missing"]
    _write(rules_path, rules)
    _refresh_checksum(package, "rules.json")

    report = validate_package(package, DEFAULT_SCHEMAS)

    codes = {issue.code for issue in report.issues}
    assert {"duplicate_id", "broken_reference"} <= codes


def test_json_schema_failure_and_mixed_content_version_are_reported(tmp_path: Path):
    package = _copy_package(tmp_path)
    conditions_path = package / "conditions.json"
    conditions = _read(conditions_path)
    conditions["content_version"] = "2.0.0"
    conditions["conditions"][0].pop("name")
    _write(conditions_path, conditions)
    _refresh_checksum(package, "conditions.json")

    report = validate_package(package, DEFAULT_SCHEMAS)

    codes = {issue.code for issue in report.issues}
    assert {"schema_validation", "version_mismatch"} <= codes


def test_checksum_and_unsupported_schema_version_are_reported(tmp_path: Path):
    package = _copy_package(tmp_path)
    with (package / "conditions.json").open("a", encoding="utf-8") as stream:
        stream.write(" ")
    manifest_path = package / "manifest.json"
    manifest = _read(manifest_path)
    manifest["schema_version"] = "9.0.0"
    _write(manifest_path, manifest)

    report = validate_package(package, DEFAULT_SCHEMAS)

    codes = {issue.code for issue in report.issues}
    assert "incompatible_schema_version" in codes
    # Manifest failure stops untrusted file traversal; checksum behavior is tested independently.
    manifest["schema_version"] = "1.0.0"
    _write(manifest_path, manifest)
    assert "checksum_mismatch" in {
        issue.code for issue in validate_package(package, DEFAULT_SCHEMAS).issues
    }


def test_invalid_schema_file_is_reported(tmp_path: Path):
    package = _copy_package(tmp_path)
    schemas = tmp_path / "schemas"
    shutil.copytree(DEFAULT_SCHEMAS, schemas)
    schema_path = schemas / "condition.schema.json"
    schema = _read(schema_path)
    schema["type"] = "not-a-json-schema-type"
    _write(schema_path, schema)

    report = validate_package(package, schemas)

    assert "invalid_schema" in {issue.code for issue in report.issues}


def test_missing_required_collection_is_reported(tmp_path: Path):
    package = _copy_package(tmp_path)
    manifest_path = package / "manifest.json"
    manifest = _read(manifest_path)
    manifest["files"] = [entry for entry in manifest["files"] if entry["name"] != "rules.json"]
    # Keep seven entries so the schema succeeds and semantic completeness is exercised.
    manifest["files"].append(dict(manifest["files"][0]))
    _write(manifest_path, manifest)

    report = validate_package(package, DEFAULT_SCHEMAS)

    codes = {issue.code for issue in report.issues}
    assert {"incomplete_package", "duplicate_file"} <= codes


def test_wrong_schema_assignment_is_rejected(tmp_path: Path):
    package = _copy_package(tmp_path)
    manifest_path = package / "manifest.json"
    manifest = _read(manifest_path)
    next(entry for entry in manifest["files"] if entry["name"] == "conditions.json")[
        "schema"
    ] = "question.schema.json"
    _write(manifest_path, manifest)

    report = validate_package(package, DEFAULT_SCHEMAS)

    assert "schema_assignment_mismatch" in {issue.code for issue in report.issues}


def test_reports_are_deterministic_and_machine_readable(tmp_path: Path):
    package = _copy_package(tmp_path)
    (package / "rules.json").unlink()

    first = validate_package(package, DEFAULT_SCHEMAS)
    second = validate_package(package, DEFAULT_SCHEMAS)

    assert first == second
    assert first.to_dict()["issues"] == second.to_dict()["issues"]
    assert list(first.issues) == sorted(
        first.issues, key=lambda item: (item.location, item.code, item.message)
    )


def test_cache_hit_change_detection_and_forced_reload(tmp_path: Path):
    package_path = _copy_package(tmp_path)
    manager = KnowledgeManager(DEFAULT_SCHEMAS)

    first = manager.load(package_path)
    assert manager.load(package_path) is first
    forced = manager.load(package_path, force=True)
    assert forced is not first
    assert forced.fingerprint == first.fingerprint

    conditions_path = package_path / "conditions.json"
    conditions = _read(conditions_path)
    conditions["conditions"][0]["summary"] += " Educational review remains appropriate."
    _write(conditions_path, conditions)
    _refresh_checksum(package_path, "conditions.json")
    changed = manager.load(package_path)
    assert changed is not forced
    assert changed.fingerprint != forced.fingerprint


def test_failed_activation_preserves_last_valid_package(tmp_path: Path):
    valid = _copy_package(tmp_path, "valid")
    invalid = _copy_package(tmp_path, "invalid")
    (invalid / "rules.json").unlink()
    manager = KnowledgeManager(DEFAULT_SCHEMAS)
    assert manager.activate(valid).valid
    previous = manager.get_active()

    report = manager.activate(invalid)

    assert not report.valid
    assert manager.get_active() is previous
    assert manager.get_status()["package_id"] == previous.package_id


def test_manager_without_active_package_fails_clearly():
    manager = KnowledgeManager(DEFAULT_SCHEMAS)
    with pytest.raises(KnowledgeLoadError, match="No valid knowledge package"):
        manager.get_active()


def test_concurrent_reads_and_activation_are_consistent(tmp_path: Path):
    package = _copy_package(tmp_path)
    manager = KnowledgeManager(DEFAULT_SCHEMAS)
    assert manager.activate(package).valid

    def read_fingerprint(_index: int) -> str:
        return manager.get_active().fingerprint

    with ThreadPoolExecutor(max_workers=8) as executor:
        fingerprints = list(executor.map(read_fingerprint, range(64)))

    assert len(set(fingerprints)) == 1


def test_factory_registers_manager_and_rejects_invalid_startup(tmp_path: Path):
    application = create_app("testing")
    assert application.extensions["knowledge"].get_active().package_id == "eye-care-en-1.0.0"

    with pytest.raises(KnowledgeLoadError, match="Unable to start"):
        create_app(
            "testing",
            {
                "KNOWLEDGE_PACKAGES_DIR": str(tmp_path),
                "KNOWLEDGE_ACTIVE_PACKAGE": "missing",
            },
        )


def test_cli_status_and_validation_json_contract(tmp_path: Path):
    application = create_app("testing")
    runner = application.test_cli_runner()
    status = runner.invoke(args=["knowledge-status", "--json"])
    assert status.exit_code == 0
    assert json.loads(status.output)["active"] is True

    invalid = _copy_package(tmp_path)
    (invalid / "rules.json").unlink()
    result = runner.invoke(args=["knowledge-validate", str(invalid), "--json"])
    payload = json.loads(result.output)
    assert result.exit_code == 1
    assert payload["valid"] is False
    assert payload["issues"]
