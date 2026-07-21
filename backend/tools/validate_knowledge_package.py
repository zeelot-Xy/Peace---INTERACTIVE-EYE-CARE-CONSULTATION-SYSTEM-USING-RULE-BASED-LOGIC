"""Validate an authored eye-care knowledge package without loading it at runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "knowledge" / "packages" / "eye-care-en-1.0.0"
DEFAULT_SCHEMAS = ROOT / "knowledge" / "schemas"

COLLECTION_KEYS = {
    "sources.json": "sources",
    "symptoms.json": "symptoms",
    "questions.json": "questions",
    "conditions.json": "conditions",
    "recommendations.json": "recommendations",
    "risk-levels.json": "risk_levels",
    "rules.json": "rules",
}

PROHIBITED_PATTERNS = {
    "diagnostic_declaration": re.compile(r"\b(?:you have|we diagnose|this confirms)\b", re.I),
    "prescribing_instruction": re.compile(
        r"\b(?:take|use|apply)\s+\d+(?:\.\d+)?\s*(?:mg|ml|drops?)\b", re.I
    ),
    "prescription_drug": re.compile(r"\b(?:antibiotic|steroid)\s+eye\s+drops?\b", re.I),
    "unsafe_delay": re.compile(
        r"\b(?:wait|delay)\s+(?:for\s+)?(?:a\s+)?(?:few|several)\s+days\b", re.I
    ),
}


@dataclass(frozen=True)
class ValidationIssue:
    """A stable, machine-readable knowledge-authoring validation result."""

    code: str
    location: str
    message: str


def _load_json(path: Path, issues: list[ValidationIssue]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(ValidationIssue("missing_file", path.name, "Required file is missing."))
    except json.JSONDecodeError as error:
        issues.append(
            ValidationIssue(
                "malformed_json",
                f"{path.name}:{error.lineno}:{error.colno}",
                error.msg,
            )
        )
    return None


def _format_path(parts: Any) -> str:
    return ".".join(str(part) for part in parts) or "$"


def _schema_validate(
    document: Any,
    schema: Any,
    filename: str,
    issues: list[ValidationIssue],
) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:  # pragma: no cover - guarded by dedicated schema test
        issues.append(ValidationIssue("invalid_schema", filename, str(error)))
        return

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        issues.append(
            ValidationIssue(
                "schema_validation",
                f"{filename}:{_format_path(error.absolute_path)}",
                error.message,
            )
        )


def _collect_fact_refs(expression: dict[str, Any]) -> set[str]:
    if "fact_id" in expression:
        return {expression["fact_id"]}
    if "not" in expression:
        return _collect_fact_refs(expression["not"])
    refs: set[str] = set()
    for key in ("all", "any"):
        for child in expression.get(key, []):
            refs.update(_collect_fact_refs(child))
    return refs


def _check_references(
    documents: dict[str, Any], issues: list[ValidationIssue]
) -> dict[str, set[str]]:
    identifiers: dict[str, set[str]] = {}
    global_locations: dict[str, str] = {}

    for filename, collection_key in COLLECTION_KEYS.items():
        identifiers[collection_key] = set()
        for index, item in enumerate(documents[filename][collection_key]):
            item_id = item["id"]
            location = f"{filename}:{collection_key}.{index}.id"
            if item_id in identifiers[collection_key]:
                issues.append(ValidationIssue("duplicate_id", location, f"Duplicate ID: {item_id}"))
            if item_id in global_locations:
                issues.append(
                    ValidationIssue(
                        "duplicate_id",
                        location,
                        f"ID also appears at {global_locations[item_id]}: {item_id}",
                    )
                )
            identifiers[collection_key].add(item_id)
            global_locations[item_id] = location

    source_ids = identifiers["sources"]
    fact_ids = identifiers["symptoms"]
    condition_ids = identifiers["conditions"]
    recommendation_ids = identifiers["recommendations"]
    risk_ids = identifiers["risk_levels"]

    for filename, collection_key in COLLECTION_KEYS.items():
        for item in documents[filename][collection_key]:
            for source_id in item.get("citation_ids", []):
                if source_id not in source_ids:
                    issues.append(
                        ValidationIssue(
                            "broken_reference",
                            f"{filename}:{item['id']}.citation_ids",
                            f"Unknown source ID: {source_id}",
                        )
                    )

    for question in documents["questions.json"]["questions"]:
        if question["fact_id"] not in fact_ids:
            issues.append(
                ValidationIssue(
                    "broken_reference",
                    f"questions.json:{question['id']}.fact_id",
                    f"Unknown fact ID: {question['fact_id']}",
                )
            )

    for rule in documents["rules.json"]["rules"]:
        location = f"rules.json:{rule['id']}"
        for fact_id in _collect_fact_refs(rule["when"]):
            if fact_id not in fact_ids:
                issues.append(
                    ValidationIssue(
                        "broken_reference", f"{location}.when", f"Unknown fact ID: {fact_id}"
                    )
                )
        for condition_id in rule["conclusion_ids"]:
            if condition_id not in condition_ids:
                issues.append(
                    ValidationIssue(
                        "broken_reference",
                        f"{location}.conclusion_ids",
                        f"Unknown condition ID: {condition_id}",
                    )
                )
        for recommendation_id in rule["recommendation_ids"]:
            if recommendation_id not in recommendation_ids:
                issues.append(
                    ValidationIssue(
                        "broken_reference",
                        f"{location}.recommendation_ids",
                        f"Unknown recommendation ID: {recommendation_id}",
                    )
                )
        if rule["risk_id"] not in risk_ids:
            issues.append(
                ValidationIssue(
                    "broken_reference",
                    f"{location}.risk_id",
                    f"Unknown risk ID: {rule['risk_id']}",
                )
            )

    return identifiers


def _iter_user_facing_text(documents: dict[str, Any]):
    fields = {
        "conditions.json": ("name", "possible_indication_label", "summary", "limitations"),
        "recommendations.json": ("title", "message"),
        "risk-levels.json": ("label", "action_window"),
        "rules.json": ("name", "rationale", "explanation_template"),
        "questions.json": ("prompt", "help_text"),
        "symptoms.json": ("label", "description"),
    }
    for filename, names in fields.items():
        collection = documents[filename][COLLECTION_KEYS[filename]]
        for item in collection:
            for name in names:
                if text := item.get(name):
                    yield filename, item["id"], name, text


def _check_safety(documents: dict[str, Any], issues: list[ValidationIssue]) -> None:
    for filename, item_id, field, value in _iter_user_facing_text(documents):
        for code, pattern in PROHIBITED_PATTERNS.items():
            if pattern.search(value):
                issues.append(
                    ValidationIssue(
                        "prohibited_wording",
                        f"{filename}:{item_id}.{field}",
                        f"Text matches prohibited pattern: {code}",
                    )
                )

    for rule in documents["rules.json"]["rules"]:
        if rule["risk_id"] == "risk_emergency":
            if rule["priority"] < 900:
                issues.append(
                    ValidationIssue(
                        "unsafe_priority",
                        f"rules.json:{rule['id']}.priority",
                        "Emergency rules must have priority 900 or higher.",
                    )
                )
            if len(rule["citation_ids"]) < 2:
                issues.append(
                    ValidationIssue(
                        "insufficient_emergency_evidence",
                        f"rules.json:{rule['id']}.citation_ids",
                        "Emergency rules require at least two sources.",
                    )
                )

    rank_by_id = {item["id"]: item["rank"] for item in documents["risk-levels.json"]["risk_levels"]}
    expected = {"risk_routine": 1, "risk_prompt": 2, "risk_urgent": 3, "risk_emergency": 4}
    if rank_by_id != expected:
        issues.append(
            ValidationIssue(
                "invalid_risk_order",
                "risk-levels.json:risk_levels",
                "Risk levels must be exactly routine=1, prompt=2, urgent=3, emergency=4.",
            )
        )


def validate_package(
    package_dir: Path = DEFAULT_PACKAGE,
    schemas_dir: Path = DEFAULT_SCHEMAS,
) -> list[ValidationIssue]:
    """Return every deterministic authoring issue found in a package."""

    package_dir = Path(package_dir)
    schemas_dir = Path(schemas_dir)
    issues: list[ValidationIssue] = []
    manifest = _load_json(package_dir / "manifest.json", issues)
    manifest_schema = _load_json(schemas_dir / "manifest.schema.json", issues)
    if manifest is None or manifest_schema is None:
        return issues
    _schema_validate(manifest, manifest_schema, "manifest.json", issues)
    if any(issue.location.startswith("manifest.json") for issue in issues):
        return issues

    documents: dict[str, Any] = {}
    for entry in manifest["files"]:
        filename = entry["name"]
        schema_name = entry["schema"]
        document_path = package_dir / filename
        document = _load_json(document_path, issues)
        schema = _load_json(schemas_dir / schema_name, issues)
        if document is None or schema is None:
            continue
        documents[filename] = document
        _schema_validate(document, schema, filename, issues)
        digest = hashlib.sha256(document_path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            issues.append(
                ValidationIssue(
                    "checksum_mismatch",
                    f"manifest.json:{filename}.sha256",
                    f"Expected {entry['sha256']}, got {digest}.",
                )
            )
        if document.get("content_version") != manifest["content_version"]:
            issues.append(
                ValidationIssue(
                    "version_mismatch",
                    f"{filename}:content_version",
                    "Content version does not match the manifest.",
                )
            )

    if set(documents) != set(COLLECTION_KEYS):
        missing = sorted(set(COLLECTION_KEYS) - set(documents))
        if missing:
            issues.append(
                ValidationIssue(
                    "incomplete_package",
                    "manifest.json:files",
                    f"Missing required collections: {', '.join(missing)}",
                )
            )
        return issues

    if any(issue.code == "schema_validation" for issue in issues):
        return issues

    _check_references(documents, issues)
    _check_safety(documents, issues)
    return sorted(issues, key=lambda item: (item.location, item.code, item.message))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--schemas", type=Path, default=DEFAULT_SCHEMAS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    issues = validate_package(args.package, args.schemas)
    if args.as_json:
        result = {"valid": not issues, "issues": [asdict(issue) for issue in issues]}
        print(json.dumps(result, indent=2))
    elif issues:
        for issue in issues:
            print(f"{issue.code}: {issue.location}: {issue.message}")
    else:
        print(f"Knowledge package is valid: {args.package}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
