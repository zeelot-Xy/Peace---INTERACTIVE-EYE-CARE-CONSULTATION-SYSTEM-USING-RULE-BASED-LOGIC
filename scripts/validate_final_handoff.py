"""Validate final audit and handoff evidence without external services."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = PROJECT_ROOT / "docs"

REQUIRED_FILES = (
    "README.md",
    "CHANGELOG.md",
    "Dockerfile",
    "docker-compose.yml",
    "compose.server.yml",
    ".env.example",
    ".env.server.example",
    "docs/academic-report.md",
    "docs/administration.md",
    "docs/api-reference.md",
    "docs/client-handoff.md",
    "docs/demo-data-and-credentials.md",
    "docs/defence-demo.md",
    "docs/final-audit-checklist.md",
    "docs/presentation-outline.md",
    "docs/security-and-privacy.md",
    "docs/server-deployment.md",
    "docs/troubleshooting.md",
    "docs/user-guide.md",
    "docs/windows-release.md",
    "scripts/build-final-handoff.ps1",
    "scripts/verify-phase14.ps1",
    "backend/examples/demo-facts-emergency.json",
    "backend/examples/demo-facts-routine.json",
)

REQUIREMENT_ROW = re.compile(
    r"^\| (?P<id>[A-Z]+-\d{3,4}) \|.*\| (?P<status>[^|]+) \|$",
    re.MULTILINE,
)
IMPLEMENTATION_MARKER = re.compile(
    r"\b(?:" + "|".join(("TO" + "DO", "FIX" + "ME", "X" + "XX")) + r")\b"
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [PROJECT_ROOT / line for line in result.stdout.splitlines() if line]


def validate_required_files(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        if not (PROJECT_ROOT / relative_path).is_file():
            errors.append(f"missing final handoff file: {relative_path}")

    for phase in range(1, 15):
        report = DOCS_ROOT / "phase-reports" / f"phase-{phase:02d}.md"
        if not report.is_file():
            errors.append(f"missing phase report: {report.relative_to(PROJECT_ROOT)}")


def validate_requirement_state(errors: list[str]) -> None:
    matrix = (DOCS_ROOT / "requirements-traceability.md").read_text(encoding="utf-8")
    report = (DOCS_ROOT / "requirements-to-test-report.md").read_text(encoding="utf-8")
    rows = list(REQUIREMENT_ROW.finditer(matrix))
    if not rows:
        errors.append("traceability matrix has no requirement rows")
        return
    for row in rows:
        requirement_id = row.group("id")
        if row.group("status").strip() != "Implemented":
            errors.append(f"requirement is not implemented: {requirement_id}")
        if f"`{requirement_id}`" not in report:
            errors.append(f"requirement lacks test evidence: {requirement_id}")


def validate_demo_fixtures(errors: list[str]) -> None:
    for name in ("demo-facts-emergency.json", "demo-facts-routine.json"):
        path = PROJECT_ROOT / "backend" / "examples" / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not payload:
            errors.append(f"demonstration fixture must be a non-empty object: {name}")
        if any(not key.startswith("fact_") for key in payload):
            errors.append(f"demonstration fixture contains a non-fact key: {name}")


def validate_tracked_hygiene(errors: list[str]) -> None:
    forbidden_parts = {
        ".env",
        ".venv",
        "node_modules",
        "__pycache__",
        "release",
        "build",
        "dist",
    }
    forbidden_suffixes = {".db", ".sqlite3", ".log"}
    marker_suffixes = {".py", ".js", ".ts", ".tsx"}

    for path in tracked_files():
        relative = path.relative_to(PROJECT_ROOT)
        if any(part in forbidden_parts for part in relative.parts):
            errors.append(f"forbidden generated or secret path is tracked: {relative}")
        if path.suffix.lower() in forbidden_suffixes:
            errors.append(f"forbidden operational file is tracked: {relative}")
        if path.suffix.lower() in marker_suffixes:
            text = path.read_text(encoding="utf-8")
            if IMPLEMENTATION_MARKER.search(text):
                errors.append(f"implementation marker remains in tracked source: {relative}")


def run() -> list[str]:
    errors: list[str] = []
    validate_required_files(errors)
    validate_requirement_state(errors)
    validate_demo_fixtures(errors)
    validate_tracked_hygiene(errors)
    return errors


def main() -> int:
    errors = run()
    if errors:
        print("Final handoff validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Final handoff validation passed: required reader set, fourteen phase reports, "
        "implemented traceability, demonstration fixtures, and tracked-file hygiene."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
