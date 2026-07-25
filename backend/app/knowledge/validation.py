"""Deterministic structural, referential, integrity, and safety validation."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from app.knowledge.contracts import ValidationIssue, ValidationReport

SUPPORTED_SCHEMA_VERSIONS = frozenset({"1.0.0"})
COLLECTION_KEYS = {
    "sources.json": "sources",
    "symptoms.json": "symptoms",
    "questions.json": "questions",
    "conditions.json": "conditions",
    "recommendations.json": "recommendations",
    "risk-levels.json": "risk_levels",
    "rules.json": "rules",
}
EXPECTED_SCHEMAS = {
    "sources.json": "source.schema.json",
    "symptoms.json": "symptom.schema.json",
    "questions.json": "question.schema.json",
    "conditions.json": "condition.schema.json",
    "recommendations.json": "recommendation.schema.json",
    "risk-levels.json": "risk-level.schema.json",
    "rules.json": "rule.schema.json",
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


def _sorted(issues: list[ValidationIssue]) -> tuple[ValidationIssue, ...]:
    return tuple(sorted(issues, key=lambda item: (item.location, item.code, item.message)))


def _load_json(path: Path, issues: list[ValidationIssue]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(ValidationIssue("missing_file", path.name, "Required file is missing."))
    except (OSError, UnicodeError) as error:
        issues.append(ValidationIssue("unreadable_file", path.name, str(error)))
    except json.JSONDecodeError as error:
        issues.append(
            ValidationIssue(
                "malformed_json", f"{path.name}:{error.lineno}:{error.colno}", error.msg
            )
        )
    return None


def _format_path(parts: Any) -> str:
    return ".".join(str(part) for part in parts) or "$"


def _schema_validate(
    document: Any, schema: Any, filename: str, issues: list[ValidationIssue]
) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:  # jsonschema exposes several schema-error subclasses
        issues.append(ValidationIssue("invalid_schema", filename, str(error)))
        return
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
    )
    for error in errors:
        issues.append(
            ValidationIssue(
                "schema_validation",
                f"{filename}:{_format_path(error.absolute_path)}",
                error.message,
            )
        )


def _fingerprint(package_dir: Path, filenames: list[str]) -> str | None:
    digest = hashlib.sha256()
    try:
        for filename in sorted(set(filenames)):
            data = _canonical_bytes(package_dir / filename)
            digest.update(filename.encode("utf-8"))
            digest.update(b"\0")
            digest.update(data)
            digest.update(b"\0")
    except OSError:
        return None
    return digest.hexdigest()


def _canonical_bytes(path: Path) -> bytes:
    """Normalize Git's platform line endings before integrity hashing."""

    return path.read_bytes().replace(b"\r\n", b"\n")


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


def _iter_predicates(expression: dict[str, Any]):
    if "fact_id" in expression:
        yield expression
        return
    if "not" in expression:
        yield from _iter_predicates(expression["not"])
        return
    for key in ("all", "any"):
        for child in expression.get(key, []):
            yield from _iter_predicates(child)


def _check_operator_operands(documents: dict[str, Any], issues: list[ValidationIssue]) -> None:
    facts = {item["id"]: item for item in documents["symptoms.json"]["symptoms"]}

    def check(expression: dict[str, Any], prefix: str) -> None:
        for predicate in _iter_predicates(expression):
            fact = facts.get(predicate["fact_id"])
            if fact is None:
                continue
            operator = predicate["operator"]
            value = predicate["value"]
            location = f"{prefix}.{predicate['fact_id']}"
            if operator in {"in", "not_in"} and not isinstance(value, list):
                issues.append(
                    ValidationIssue(
                        "invalid_operator_operand",
                        location,
                        f"Operator '{operator}' requires an array value.",
                    )
                )
            if operator not in {"in", "not_in"} and isinstance(value, list):
                issues.append(
                    ValidationIssue(
                        "invalid_operator_operand",
                        location,
                        f"Operator '{operator}' requires a scalar value.",
                    )
                )
            if operator in {"gt", "gte", "lt", "lte"} and (
                fact["value_type"] != "integer" or type(value) is not int
            ):
                issues.append(
                    ValidationIssue(
                        "invalid_operator_operand",
                        location,
                        f"Operator '{operator}' is limited to integer facts and values.",
                    )
                )

    for rule in documents["rules.json"]["rules"]:
        check(rule["when"], f"rules.json:{rule['id']}.when")
    for question in documents["questions.json"]["questions"]:
        if "show_when" in question:
            check(
                question["show_when"],
                f"questions.json:{question['id']}.show_when",
            )


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

    for filename, collection_key in COLLECTION_KEYS.items():
        for item in documents[filename][collection_key]:
            for source_id in item.get("citation_ids", []):
                if source_id not in identifiers["sources"]:
                    issues.append(
                        ValidationIssue(
                            "broken_reference",
                            f"{filename}:{item['id']}.citation_ids",
                            f"Unknown source ID: {source_id}",
                        )
                    )
    for question in documents["questions.json"]["questions"]:
        if question["fact_id"] not in identifiers["symptoms"]:
            issues.append(
                ValidationIssue(
                    "broken_reference",
                    f"questions.json:{question['id']}.fact_id",
                    f"Unknown fact ID: {question['fact_id']}",
                )
            )
        if "show_when" in question:
            for fact_id in _collect_fact_refs(question["show_when"]):
                if fact_id not in identifiers["symptoms"]:
                    issues.append(
                        ValidationIssue(
                            "broken_reference",
                            f"questions.json:{question['id']}.show_when",
                            f"Unknown fact ID: {fact_id}",
                        )
                    )
    for rule in documents["rules.json"]["rules"]:
        location = f"rules.json:{rule['id']}"
        for fact_id in _collect_fact_refs(rule["when"]):
            if fact_id not in identifiers["symptoms"]:
                issues.append(
                    ValidationIssue(
                        "broken_reference", f"{location}.when", f"Unknown fact ID: {fact_id}"
                    )
                )
        reference_sets = (
            ("conclusion_ids", "conditions"),
            ("recommendation_ids", "recommendations"),
        )
        for field, collection in reference_sets:
            for item_id in rule[field]:
                if item_id not in identifiers[collection]:
                    issues.append(
                        ValidationIssue(
                            "broken_reference",
                            f"{location}.{field}",
                            f"Unknown {collection.rstrip('s')} ID: {item_id}",
                        )
                    )
        if rule["risk_id"] not in identifiers["risk_levels"]:
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
        for item in documents[filename][COLLECTION_KEYS[filename]]:
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
    ranks = {item["id"]: item["rank"] for item in documents["risk-levels.json"]["risk_levels"]}
    expected = {"risk_routine": 1, "risk_prompt": 2, "risk_urgent": 3, "risk_emergency": 4}
    if ranks != expected:
        issues.append(
            ValidationIssue(
                "invalid_risk_order",
                "risk-levels.json:risk_levels",
                "Risk levels must be exactly routine=1, prompt=2, urgent=3, emergency=4.",
            )
        )


def validate_package_data(
    package_dir: Path, schemas_dir: Path
) -> tuple[ValidationReport, dict[str, Any] | None, dict[str, Any]]:
    """Validate and return the report plus raw manifest/documents for trusted callers."""

    package_dir = Path(package_dir).resolve()
    schemas_dir = Path(schemas_dir).resolve()
    issues: list[ValidationIssue] = []
    manifest = _load_json(package_dir / "manifest.json", issues)
    manifest_schema = _load_json(schemas_dir / "manifest.schema.json", issues)
    metadata = manifest if isinstance(manifest, dict) else {}
    filenames = ["manifest.json"]
    if isinstance(manifest, dict) and isinstance(manifest.get("files"), list):
        for entry in manifest["files"]:
            name = entry.get("name") if isinstance(entry, dict) else None
            if isinstance(name, str) and Path(name).name == name:
                filenames.append(name)
    fingerprint = _fingerprint(package_dir, filenames)

    if manifest is None or manifest_schema is None:
        report = ValidationReport(
            False,
            metadata.get("package_id"),
            metadata.get("schema_version"),
            metadata.get("content_version"),
            fingerprint,
            _sorted(issues),
        )
        return report, None, {}

    schema_version = manifest.get("schema_version") if isinstance(manifest, dict) else None
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        issues.append(
            ValidationIssue(
                "incompatible_schema_version",
                "manifest.json:schema_version",
                f"Unsupported schema version: {schema_version!r}.",
            )
        )
    _schema_validate(manifest, manifest_schema, "manifest.json", issues)
    if any(issue.location.startswith("manifest.json") for issue in issues):
        report = ValidationReport(
            False,
            metadata.get("package_id"),
            schema_version,
            metadata.get("content_version"),
            fingerprint,
            _sorted(issues),
        )
        return report, manifest, {}

    documents: dict[str, Any] = {}
    declared_names = [entry["name"] for entry in manifest["files"]]
    for filename in sorted(set(declared_names)):
        if declared_names.count(filename) > 1:
            issues.append(
                ValidationIssue(
                    "duplicate_file",
                    "manifest.json:files",
                    f"File is declared more than once: {filename}",
                )
            )
    for entry in manifest["files"]:
        filename = entry["name"]
        expected_schema = EXPECTED_SCHEMAS.get(filename)
        if expected_schema and entry["schema"] != expected_schema:
            issues.append(
                ValidationIssue(
                    "schema_assignment_mismatch",
                    f"manifest.json:{filename}.schema",
                    f"Expected schema {expected_schema}, got {entry['schema']}.",
                )
            )
        document_path = package_dir / filename
        document = _load_json(document_path, issues)
        schema = _load_json(schemas_dir / entry["schema"], issues)
        if document is None or schema is None:
            continue
        documents[filename] = document
        _schema_validate(document, schema, filename, issues)
        try:
            digest = hashlib.sha256(_canonical_bytes(document_path)).hexdigest()
        except OSError:
            continue
        if digest != entry["sha256"]:
            issues.append(
                ValidationIssue(
                    "checksum_mismatch",
                    f"manifest.json:{filename}.sha256",
                    f"Expected {entry['sha256']}, got {digest}.",
                )
            )
        if (
            isinstance(document, dict)
            and document.get("content_version") != manifest["content_version"]
        ):
            issues.append(
                ValidationIssue(
                    "version_mismatch",
                    f"{filename}:content_version",
                    "Content version does not match the manifest.",
                )
            )

    if set(documents) != set(COLLECTION_KEYS):
        missing = sorted(set(COLLECTION_KEYS) - set(documents))
        unexpected = sorted(set(documents) - set(COLLECTION_KEYS))
        if missing:
            issues.append(
                ValidationIssue(
                    "incomplete_package",
                    "manifest.json:files",
                    f"Missing required collections: {', '.join(missing)}",
                )
            )
        if unexpected:
            issues.append(
                ValidationIssue(
                    "unexpected_collection",
                    "manifest.json:files",
                    f"Unexpected collections: {', '.join(unexpected)}",
                )
            )
    elif not any(issue.code in {"schema_validation", "invalid_schema"} for issue in issues):
        _check_references(documents, issues)
        _check_operator_operands(documents, issues)
        _check_safety(documents, issues)

    sorted_issues = _sorted(issues)
    report = ValidationReport(
        not sorted_issues,
        manifest.get("package_id"),
        manifest.get("schema_version"),
        manifest.get("content_version"),
        fingerprint,
        sorted_issues,
    )
    return report, manifest, documents


def validate_package(package_dir: Path, schemas_dir: Path) -> ValidationReport:
    """Return a deterministic validation report without activating the package."""

    return validate_package_data(package_dir, schemas_dir)[0]
