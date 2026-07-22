"""Immutable contracts exposed by the runtime knowledge subsystem."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True, order=True)
class ValidationIssue:
    """A stable, machine-readable validation failure."""

    code: str
    location: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """Deterministic result of validating one package candidate."""

    valid: bool
    package_id: str | None
    schema_version: str | None
    content_version: str | None
    fingerprint: str | None
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "package_id": self.package_id,
            "schema_version": self.schema_version,
            "content_version": self.content_version,
            "fingerprint": self.fingerprint,
            "issues": [asdict(issue) for issue in self.issues],
        }


def freeze(value: Any) -> Any:
    """Recursively convert JSON-compatible data into read-only values."""

    if isinstance(value, dict):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class KnowledgePackage:
    """A validated, deeply immutable knowledge package snapshot."""

    path: Path
    fingerprint: str
    manifest: Mapping[str, Any]
    collections: Mapping[str, tuple[Mapping[str, Any], ...]]
    indexes: Mapping[str, Mapping[str, Mapping[str, Any]]]

    @property
    def package_id(self) -> str:
        return str(self.manifest["package_id"])

    @property
    def schema_version(self) -> str:
        return str(self.manifest["schema_version"])

    @property
    def content_version(self) -> str:
        return str(self.manifest["content_version"])
