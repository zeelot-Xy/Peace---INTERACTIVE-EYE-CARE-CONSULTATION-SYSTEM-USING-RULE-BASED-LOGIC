"""Thread-safe runtime loading, caching, and atomic knowledge activation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from types import MappingProxyType
from typing import Any

from app.knowledge.contracts import KnowledgePackage, ValidationReport, freeze
from app.knowledge.exceptions import KnowledgeLoadError
from app.knowledge.validation import COLLECTION_KEYS, validate_package, validate_package_data


@dataclass(frozen=True)
class _CacheEntry:
    signature: tuple[tuple[str, int, int], ...]
    package: KnowledgePackage


class KnowledgeManager:
    """Own the process-local last-known-valid knowledge snapshot."""

    def __init__(self, schemas_dir: Path):
        self.schemas_dir = Path(schemas_dir).resolve()
        self._lock = RLock()
        self._cache: dict[Path, _CacheEntry] = {}
        self._active: KnowledgePackage | None = None
        self._active_path: Path | None = None
        self._last_report: ValidationReport | None = None

    def _signature(self, package_path: Path) -> tuple[tuple[str, int, int], ...]:
        paths = [package_path / "manifest.json", *sorted(self.schemas_dir.glob("*.schema.json"))]
        try:
            manifest = json.loads((package_path / "manifest.json").read_text("utf-8"))
            declared = manifest.get("files", [])
            entries = declared if isinstance(declared, list) else ()
        except (AttributeError, OSError, ValueError, TypeError, KeyError):
            entries = ()
        for entry in entries:
            name = entry.get("name") if isinstance(entry, dict) else None
            if isinstance(name, str) and Path(name).name == name:
                paths.append(package_path / name)
        signature = []
        for path in sorted(set(paths), key=lambda item: str(item)):
            try:
                stat = path.stat()
                signature.append((str(path), stat.st_size, stat.st_mtime_ns))
            except OSError:
                signature.append((str(path), -1, -1))
        return tuple(signature)

    def validate(self, package_path: Path) -> ValidationReport:
        return validate_package(Path(package_path).resolve(), self.schemas_dir)

    def load(self, package_path: Path, *, force: bool = False) -> KnowledgePackage:
        path = Path(package_path).resolve()
        with self._lock:
            signature = self._signature(path)
            cached = self._cache.get(path)
            if not force and cached and cached.signature == signature:
                return cached.package
            report, manifest, documents = validate_package_data(path, self.schemas_dir)
            self._last_report = report
            if not report.valid or manifest is None:
                codes = ", ".join(sorted({issue.code for issue in report.issues}))
                raise KnowledgeLoadError(f"Knowledge package '{path.name}' is invalid: {codes}.")
            collections: dict[str, Any] = {}
            indexes: dict[str, Any] = {}
            for filename, collection_key in COLLECTION_KEYS.items():
                items = tuple(freeze(item) for item in documents[filename][collection_key])
                collections[collection_key] = items
                indexes[collection_key] = MappingProxyType({item["id"]: item for item in items})
            package = KnowledgePackage(
                path=path,
                fingerprint=report.fingerprint or "",
                manifest=freeze(manifest),
                collections=MappingProxyType(collections),
                indexes=MappingProxyType(indexes),
            )
            self._cache[path] = _CacheEntry(signature, package)
            return package

    def activate(self, package_path: Path, *, force: bool = False) -> ValidationReport:
        path = Path(package_path).resolve()
        with self._lock:
            try:
                candidate = self.load(path, force=force)
            except KnowledgeLoadError:
                assert self._last_report is not None
                return self._last_report
            self._active = candidate
            self._active_path = path
            self._last_report = ValidationReport(
                True,
                candidate.package_id,
                candidate.schema_version,
                candidate.content_version,
                candidate.fingerprint,
                (),
            )
            return self._last_report

    def get_active(self) -> KnowledgePackage:
        with self._lock:
            if self._active is None:
                raise KnowledgeLoadError("No valid knowledge package is active.")
            return self._active

    def reload_if_changed(self) -> ValidationReport:
        with self._lock:
            if self._active_path is None:
                raise KnowledgeLoadError("No knowledge package path is configured for reload.")
            return self.activate(self._active_path)

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            active = self._active
            return {
                "active": active is not None,
                "package_id": active.package_id if active else None,
                "schema_version": active.schema_version if active else None,
                "content_version": active.content_version if active else None,
                "fingerprint": active.fingerprint if active else None,
                "path": str(active.path) if active else None,
                "manifest_status": active.manifest["status"] if active else None,
                "last_validation": self._last_report.to_dict() if self._last_report else None,
            }
