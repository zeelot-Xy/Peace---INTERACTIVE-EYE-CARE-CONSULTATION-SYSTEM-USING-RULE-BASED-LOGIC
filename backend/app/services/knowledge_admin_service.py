"""Administrator validation, publication, retention, and rollback workflows."""

from __future__ import annotations

import io
import json
import os
import shutil
import stat
import uuid
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from flask import current_app
from werkzeug.datastructures import FileStorage

from app.extensions import db
from app.knowledge import KnowledgePackage
from app.knowledge.validation import COLLECTION_KEYS
from app.models import KnowledgeVersion
from app.services.audit_service import record_audit


class KnowledgeAdminError(RuntimeError):
    def __init__(self, message: str, code: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def _plain(value: Any) -> Any:
    if isinstance(value, dict) or hasattr(value, "items"):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _version_payload(version: KnowledgeVersion) -> dict[str, Any]:
    return {
        "id": version.id,
        "package_id": version.package_id,
        "schema_version": version.schema_version,
        "content_version": version.content_version,
        "fingerprint": version.fingerprint,
        "title": version.title,
        "status": version.status,
        "is_valid": version.is_valid,
        "is_active": version.is_active,
        "validation_report": version.validation_report,
        "diff_summary": version.diff_summary,
        "uploaded_at": version.uploaded_at.isoformat() if version.uploaded_at else None,
        "published_at": version.published_at.isoformat() if version.published_at else None,
        "retired_at": version.retired_at.isoformat() if version.retired_at else None,
    }


def ensure_active_version() -> KnowledgeVersion:
    package = current_app.extensions["knowledge"].get_active()
    existing = db.session.scalar(
        db.select(KnowledgeVersion).where(
            KnowledgeVersion.fingerprint == package.fingerprint
        )
    )
    if existing:
        if not existing.is_active:
            db.session.execute(
                db.update(KnowledgeVersion).values(is_active=False)
            )
            existing.is_active = True
            existing.status = "published"
            db.session.commit()
        return existing
    version = KnowledgeVersion(
        package_id=package.package_id,
        schema_version=package.schema_version,
        content_version=package.content_version,
        fingerprint=package.fingerprint,
        title=str(package.manifest["title"]),
        status="published",
        is_valid=True,
        is_active=True,
        storage_path=str(package.path),
        validation_report={
            "valid": True,
            "package_id": package.package_id,
            "schema_version": package.schema_version,
            "content_version": package.content_version,
            "fingerprint": package.fingerprint,
            "issues": [],
        },
        diff_summary=None,
        published_at=datetime.now(UTC),
    )
    db.session.add(version)
    db.session.commit()
    return version


def list_versions() -> list[dict[str, Any]]:
    ensure_active_version()
    versions = db.session.scalars(
        db.select(KnowledgeVersion).order_by(KnowledgeVersion.uploaded_at.desc())
    ).all()
    return [_version_payload(version) for version in versions]


def get_version(version_id: str) -> dict[str, Any]:
    version = db.session.get(KnowledgeVersion, version_id)
    if version is None:
        raise KnowledgeAdminError("Knowledge version was not found.", "not_found", 404)
    return _version_payload(version)


def _archive_files(data: bytes) -> dict[str, bytes]:
    expected = {"manifest.json", *COLLECTION_KEYS}
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as error:
        raise KnowledgeAdminError(
            "The uploaded file is not a valid ZIP archive.",
            "invalid_archive",
            422,
        ) from error
    with archive:
        files = [entry for entry in archive.infolist() if not entry.is_dir()]
        if not files:
            raise KnowledgeAdminError("The archive is empty.", "invalid_archive", 422)
        if sum(entry.file_size for entry in files) > current_app.config[
            "KNOWLEDGE_UPLOAD_MAX_BYTES"
        ]:
            raise KnowledgeAdminError(
                "The extracted knowledge package is too large.",
                "package_too_large",
                413,
            )
        paths = [PurePosixPath(entry.filename.replace("\\", "/")) for entry in files]
        if any(
            path.is_absolute()
            or ".." in path.parts
            or stat.S_ISLNK(entry.external_attr >> 16)
            for path, entry in zip(paths, files, strict=True)
        ):
            raise KnowledgeAdminError(
                "The archive contains an unsafe path or link.",
                "unsafe_archive",
                422,
            )
        strip_root = (
            len({path.parts[0] for path in paths}) == 1
            and all(len(path.parts) > 1 for path in paths)
        )
        normalized = [
            "/".join(path.parts[1:] if strip_root else path.parts) for path in paths
        ]
        if set(normalized) != expected or len(normalized) != len(expected):
            raise KnowledgeAdminError(
                "A complete package must contain only manifest.json and the seven "
                "required collections.",
                "incomplete_package",
                422,
            )
        return {
            name: archive.read(entry)
            for name, entry in zip(normalized, files, strict=True)
        }


def _rule_refs(rule: Any) -> set[str]:
    refs = {
        *rule.get("conclusion_ids", ()),
        *rule.get("recommendation_ids", ()),
        rule.get("risk_id"),
    }

    def walk(expression: Any) -> None:
        if "fact_id" in expression:
            refs.add(expression["fact_id"])
        if "not" in expression:
            walk(expression["not"])
        for key in ("all", "any"):
            for child in expression.get(key, ()):
                walk(child)

    walk(rule["when"])
    return {item for item in refs if item}


def _diff(active: KnowledgePackage, candidate: KnowledgePackage) -> dict[str, Any]:
    collections: dict[str, Any] = {}
    changed_ids: set[str] = set()
    for name in COLLECTION_KEYS.values():
        before = {item_id: _plain(item) for item_id, item in active.indexes[name].items()}
        after = {
            item_id: _plain(item) for item_id, item in candidate.indexes[name].items()
        }
        added = sorted(set(after) - set(before))
        removed = sorted(set(before) - set(after))
        changed = sorted(
            item_id
            for item_id in set(before) & set(after)
            if before[item_id] != after[item_id]
        )
        changed_ids.update(added)
        changed_ids.update(removed)
        changed_ids.update(changed)
        collections[name] = {
            "before": len(before),
            "after": len(after),
            "added": added,
            "removed": removed,
            "changed": changed,
        }
    affected_rules = set(collections["rules"]["added"])
    affected_rules.update(collections["rules"]["removed"])
    affected_rules.update(collections["rules"]["changed"])
    for package in (active, candidate):
        for rule in package.collections["rules"]:
            if _rule_refs(rule) & changed_ids:
                affected_rules.add(rule["id"])
    warnings = []
    if candidate.manifest["status"] not in {"reviewed", "published"}:
        warnings.append(
            "The manifest is valid but is not marked reviewed or published."
        )
    return {
        "active_fingerprint": active.fingerprint,
        "candidate_fingerprint": candidate.fingerprint,
        "collections": collections,
        "affected_rule_ids": sorted(affected_rules),
        "warnings": warnings,
    }


def validate_upload(file: FileStorage | None, actor_user_id: str) -> dict[str, Any]:
    ensure_active_version()
    if file is None or not file.filename:
        raise KnowledgeAdminError(
            "Choose a complete knowledge-package ZIP file.",
            "file_required",
            422,
        )
    if not file.filename.lower().endswith(".zip"):
        raise KnowledgeAdminError("Knowledge packages must be ZIP files.", "invalid_file_type", 422)
    limit = current_app.config["KNOWLEDGE_UPLOAD_MAX_BYTES"]
    data = file.stream.read(limit + 1)
    if len(data) > limit:
        raise KnowledgeAdminError("The uploaded package is too large.", "package_too_large", 413)
    files = _archive_files(data)
    packages_dir = Path(current_app.config["KNOWLEDGE_PACKAGES_DIR"])
    staging = packages_dir / f".incoming-{uuid.uuid4()}"
    staging.mkdir(parents=True, exist_ok=False)
    try:
        for name, content in files.items():
            (staging / name).write_bytes(content)
        manager = current_app.extensions["knowledge"]
        report = manager.validate(staging)
        if not report.valid:
            version = KnowledgeVersion(
                status="invalid",
                is_valid=False,
                is_active=False,
                validation_report=report.to_dict(),
                uploaded_by_user_id=actor_user_id,
            )
            db.session.add(version)
            record_audit(
                "knowledge.validate_failed",
                actor_user_id=actor_user_id,
                resource_type="knowledge_version",
                resource_id=version.id,
                event_data={"issue_codes": sorted({item.code for item in report.issues})},
            )
            db.session.commit()
            return _version_payload(version)

        if db.session.scalar(
            db.select(KnowledgeVersion).where(
                (KnowledgeVersion.package_id == report.package_id)
                | (KnowledgeVersion.fingerprint == report.fingerprint)
            )
        ):
            raise KnowledgeAdminError(
                "This package ID or fingerprint is already retained.",
                "duplicate_knowledge_version",
                409,
            )
        destination = packages_dir / str(report.package_id)
        if destination.exists():
            raise KnowledgeAdminError(
                "The package directory already exists and will not be overwritten.",
                "duplicate_knowledge_version",
                409,
            )
        candidate = manager.load(staging)
        diff = _diff(manager.get_active(), candidate)
        shutil.move(str(staging), destination)
        version = KnowledgeVersion(
            package_id=report.package_id,
            schema_version=report.schema_version,
            content_version=report.content_version,
            fingerprint=report.fingerprint,
            title=str(candidate.manifest["title"]),
            status="validated",
            is_valid=True,
            is_active=False,
            storage_path=str(destination),
            validation_report=report.to_dict(),
            diff_summary=diff,
            uploaded_by_user_id=actor_user_id,
        )
        db.session.add(version)
        record_audit(
            "knowledge.validate",
            actor_user_id=actor_user_id,
            resource_type="knowledge_version",
            resource_id=version.id,
            event_data={
                "package_id": report.package_id,
                "fingerprint": report.fingerprint,
                "affected_rule_count": len(diff["affected_rule_ids"]),
            },
        )
        db.session.commit()
        return _version_payload(version)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _write_active_state(package_id: str, fingerprint: str) -> None:
    state_file = Path(current_app.config["KNOWLEDGE_STATE_FILE"])
    state_file.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_file.with_name(f".{state_file.name}.{uuid.uuid4()}.tmp")
    try:
        temporary.write_text(
            json.dumps(
                {"package_id": package_id, "fingerprint": fingerprint},
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, state_file)
    finally:
        temporary.unlink(missing_ok=True)


def activate_version(
    version_id: str, actor_user_id: str, *, rollback: bool = False
) -> dict[str, Any]:
    ensure_active_version()
    version = db.session.get(KnowledgeVersion, version_id)
    if version is None:
        raise KnowledgeAdminError("Knowledge version was not found.", "not_found", 404)
    if not version.is_valid or not version.storage_path:
        raise KnowledgeAdminError(
            "Only a valid retained package can be published.",
            "invalid_knowledge_version",
            409,
        )
    if version.is_active:
        raise KnowledgeAdminError(
            "This knowledge version is already active.",
            "knowledge_version_active",
            409,
        )
    manager = current_app.extensions["knowledge"]
    previous = db.session.scalar(
        db.select(KnowledgeVersion).where(KnowledgeVersion.is_active.is_(True))
    )
    report = manager.activate(Path(version.storage_path), force=True)
    if not report.valid:
        raise KnowledgeAdminError(
            "The retained package no longer passes validation.",
            "knowledge_revalidation_failed",
            409,
        )
    try:
        _write_active_state(str(version.package_id), str(version.fingerprint))
        now = datetime.now(UTC)
        if previous:
            previous.is_active = False
            previous.status = "retired"
            previous.retired_at = now
        version.is_active = True
        version.status = "published"
        version.published_at = now
        version.retired_at = None
        action = "knowledge.rollback" if rollback else "knowledge.publish"
        record_audit(
            action,
            actor_user_id=actor_user_id,
            resource_type="knowledge_version",
            resource_id=version.id,
            event_data={
                "package_id": version.package_id,
                "fingerprint": version.fingerprint,
                "previous_version_id": previous.id if previous else None,
            },
        )
        db.session.commit()
    except Exception:
        db.session.rollback()
        if previous and previous.storage_path:
            manager.activate(Path(previous.storage_path), force=True)
            _write_active_state(
                str(previous.package_id),
                str(previous.fingerprint),
            )
        raise
    return _version_payload(version)
