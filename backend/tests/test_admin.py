from __future__ import annotations

import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import AuditLog, User
from tools.validate_knowledge_package import DEFAULT_PACKAGE, DEFAULT_SCHEMAS


def _register(client, email: str = "admin@example.com"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "System Administrator",
            "email": email,
            "password": "a secure administrator password",
        },
    )


def _csrf(client) -> dict[str, str]:
    return {"X-CSRF-TOKEN": client.get_cookie("csrf_access_token").value}


def _login_as_admin(application, client):
    assert _register(client).status_code == 201
    with application.app_context():
        user = db.session.scalar(db.select(User))
        user.role = "admin"
        db.session.commit()
    assert client.post("/api/v1/auth/logout", headers=_csrf(client)).status_code == 200
    assert (
        client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@example.com",
                "password": "a secure administrator password",
            },
        ).status_code
        == 200
    )


def _write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _candidate_archive(tmp_path: Path) -> bytes:
    package = tmp_path / "candidate"
    shutil.copytree(DEFAULT_PACKAGE, package)
    manifest_path = package / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["package_id"] = "eye-care-en-1.0.1"
    manifest["content_version"] = "1.0.1"
    manifest["status"] = "reviewed"
    for filename in (
        "conditions.json",
        "questions.json",
        "recommendations.json",
        "risk-levels.json",
        "rules.json",
        "sources.json",
        "symptoms.json",
    ):
        path = package / filename
        document = json.loads(path.read_text(encoding="utf-8"))
        document["content_version"] = "1.0.1"
        if filename == "rules.json":
            document["rules"][0]["rationale"] += " Reviewed for Phase 8."
        _write_json(path, document)
        digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        next(item for item in manifest["files"] if item["name"] == filename)[
            "sha256"
        ] = digest
    _write_json(manifest_path, manifest)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package.glob("*.json")):
            archive.write(path, path.name)
    return stream.getvalue()


def _admin_app(tmp_path: Path):
    packages = tmp_path / "packages"
    packages.mkdir()
    shutil.copytree(DEFAULT_PACKAGE, packages / DEFAULT_PACKAGE.name)
    application = create_app(
        "testing",
        {
            "KNOWLEDGE_PACKAGES_DIR": str(packages),
            "KNOWLEDGE_SCHEMAS_DIR": str(DEFAULT_SCHEMAS),
            "KNOWLEDGE_STATE_FILE": str(tmp_path / "active.json"),
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        },
    )
    with application.app_context():
        db.create_all()
    return application


def test_patient_is_denied_all_administrator_summary_access(client):
    assert _register(client, "patient@example.com").status_code == 201

    response = client.get("/api/v1/admin/summary")

    assert response.status_code == 403
    assert response.get_json()["errors"][0]["code"] == "forbidden"


def test_admin_summary_consultations_reports_and_audit_are_safe(app, client):
    _login_as_admin(app, client)
    consultation = client.post("/api/v1/consultations", headers=_csrf(client))
    consultation_id = consultation.get_json()["data"]["consultation"]["id"]

    summary = client.get("/api/v1/admin/summary")
    consultations = client.get("/api/v1/admin/consultations")
    report = client.get(f"/api/v1/admin/consultations/{consultation_id}/report")
    audits = client.get("/api/v1/admin/audit-logs")

    assert summary.status_code == 200
    assert summary.get_json()["data"]["summary"]["users"]["administrators"] == 1
    assert consultations.get_json()["data"]["items"][0]["patient"]["email"] == "admin@example.com"
    assert report.get_json()["data"]["report"]["result"] is None
    assert audits.get_json()["data"]["items"]
    assert "password" not in json.dumps(audits.get_json()).lower()


def test_validated_publish_and_rollback_preserve_frozen_consultations(tmp_path: Path):
    application = _admin_app(tmp_path)
    client = application.test_client()
    _login_as_admin(application, client)
    original = client.get("/api/v1/admin/knowledge").get_json()["data"]["items"][0]
    consultation = client.post("/api/v1/consultations", headers=_csrf(client))
    consultation_id = consultation.get_json()["data"]["consultation"]["id"]

    invalid = client.post(
        "/api/v1/admin/knowledge/validate",
        data={"package": (io.BytesIO(b"not a zip"), "invalid.zip")},
        headers=_csrf(client),
        content_type="multipart/form-data",
    )
    assert invalid.status_code == 422
    with application.app_context():
        assert application.extensions["knowledge"].get_active().package_id == original["package_id"]

    validated = client.post(
        "/api/v1/admin/knowledge/validate",
        data={
            "package": (
                io.BytesIO(_candidate_archive(tmp_path)),
                "eye-care-en-1.0.1.zip",
            )
        },
        headers=_csrf(client),
        content_type="multipart/form-data",
    )
    assert validated.status_code == 201
    candidate = validated.get_json()["data"]["version"]
    assert candidate["status"] == "validated"
    assert candidate["diff_summary"]["affected_rule_ids"]

    published = client.post(
        f"/api/v1/admin/knowledge/{candidate['id']}/publish",
        headers=_csrf(client),
    )
    assert published.status_code == 200
    assert published.get_json()["data"]["version"]["is_active"] is True
    restarted = create_app(
        "testing",
        {
            "KNOWLEDGE_PACKAGES_DIR": str(tmp_path / "packages"),
            "KNOWLEDGE_SCHEMAS_DIR": str(DEFAULT_SCHEMAS),
            "KNOWLEDGE_STATE_FILE": str(tmp_path / "active.json"),
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        },
    )
    assert restarted.extensions["knowledge"].get_active().package_id == "eye-care-en-1.0.1"
    frozen = client.get(f"/api/v1/consultations/{consultation_id}")
    assert frozen.get_json()["data"]["consultation"]["knowledge"]["package_id"] == original[
        "package_id"
    ]

    rolled_back = client.post(
        f"/api/v1/admin/knowledge/{original['id']}/rollback",
        headers=_csrf(client),
    )
    assert rolled_back.status_code == 200
    with application.app_context():
        assert application.extensions["knowledge"].get_active().package_id == original["package_id"]
        actions = set(db.session.scalars(db.select(AuditLog.action)).all())
        assert {"knowledge.validate", "knowledge.publish", "knowledge.rollback"} <= actions
    assert (tmp_path / "active.json").exists()

    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
