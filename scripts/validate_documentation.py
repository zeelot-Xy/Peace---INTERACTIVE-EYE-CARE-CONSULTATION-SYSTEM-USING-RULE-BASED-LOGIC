"""Validate the final documentation set without requiring application dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = PROJECT_ROOT / "docs"
SOURCES_FILE = (
    PROJECT_ROOT
    / "backend"
    / "knowledge"
    / "packages"
    / "eye-care-en-1.0.0"
    / "sources.json"
)

REQUIRED_DOCUMENTS = (
    "README.md",
    "academic-report.md",
    "academic-report-outline.md",
    "api-reference.md",
    "architecture/diagrams.md",
    "development.md",
    "testing.md",
    "troubleshooting.md",
    "user-guide.md",
    "academic/phase-13-methodology.md",
    "phase-reports/phase-13.md",
)

REQUIRED_REPORT_HEADINGS = (
    "# Development of an Interactive Eye Care Consultation System Using Rule-Based Logic",
    "## Abstract",
    "## Chapter One: Introduction",
    "## Chapter Two: Literature Review",
    "## Chapter Three: Methodology and System Design",
    "## Chapter Four: Implementation, Testing, and Results",
    "## Chapter Five: Summary, Conclusion, and Recommendations",
    "## References",
    "## Appendices",
)

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#", "data:")


def markdown_files() -> list[Path]:
    return [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        *sorted(DOCS_ROOT.rglob("*.md")),
    ]


def validate_required_documents(errors: list[str]) -> None:
    for relative_path in REQUIRED_DOCUMENTS:
        path = DOCS_ROOT / relative_path
        if not path.is_file():
            errors.append(f"missing required document: docs/{relative_path}")


def validate_local_links(errors: list[str]) -> None:
    for markdown_path in markdown_files():
        text = markdown_path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.lower().startswith(EXTERNAL_PREFIXES):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (markdown_path.parent / path_part).resolve()
            if not resolved.exists():
                display = markdown_path.relative_to(PROJECT_ROOT)
                errors.append(f"broken local link in {display}: {target}")


def validate_academic_report(errors: list[str]) -> None:
    report_path = DOCS_ROOT / "academic-report.md"
    if not report_path.is_file():
        return
    report = report_path.read_text(encoding="utf-8")
    for heading in REQUIRED_REPORT_HEADINGS:
        if heading not in report:
            errors.append(f"academic report missing heading: {heading}")

    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))["sources"]
    for source in sources:
        if source["id"] not in report:
            errors.append(f"academic report missing source ID: {source['id']}")


def validate_index(errors: list[str]) -> None:
    index_path = DOCS_ROOT / "README.md"
    if not index_path.is_file():
        return
    index = index_path.read_text(encoding="utf-8")
    for relative_path in REQUIRED_DOCUMENTS:
        if relative_path == "README.md":
            continue
        if f"({relative_path})" not in index:
            errors.append(f"documentation index missing: {relative_path}")


def run() -> list[str]:
    errors: list[str] = []
    validate_required_documents(errors)
    validate_local_links(errors)
    validate_academic_report(errors)
    validate_index(errors)
    return errors


def main() -> int:
    errors = run()
    if errors:
        print("Documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Documentation validation passed: {len(markdown_files())} Markdown files, "
        f"{len(REQUIRED_DOCUMENTS)} required deliverables, and complete source coverage."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

