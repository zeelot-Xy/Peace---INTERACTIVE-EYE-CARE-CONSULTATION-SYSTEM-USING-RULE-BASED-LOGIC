"""Validate an authored eye-care knowledge package using the runtime validator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.knowledge.contracts import ValidationIssue  # noqa: E402
from app.knowledge.validation import validate_package as build_validation_report  # noqa: E402

DEFAULT_PACKAGE = ROOT / "knowledge" / "packages" / "eye-care-en-1.0.0"
DEFAULT_SCHEMAS = ROOT / "knowledge" / "schemas"


def validate_package(
    package_dir: Path = DEFAULT_PACKAGE, schemas_dir: Path = DEFAULT_SCHEMAS
) -> list[ValidationIssue]:
    """Preserve the Phase 3 authoring API while sharing runtime validation logic."""

    return list(build_validation_report(package_dir, schemas_dir).issues)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--schemas", type=Path, default=DEFAULT_SCHEMAS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = build_validation_report(args.package, args.schemas)
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    elif report.issues:
        for issue in report.issues:
            print(f"{issue.code}: {issue.location}: {issue.message}")
    else:
        print(f"Knowledge package is valid: {args.package}")
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
