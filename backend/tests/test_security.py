import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from app.models import AuditLog, RefreshToken, User
from app.services.audit_service import record_audit


def _registration(email: str = "security@example.com") -> dict[str, str]:
    return {
        "full_name": "Security Example",
        "email": email,
        "password": "correct horse battery staple",
    }


def test_api_responses_include_defensive_headers(client):
    response = client.get("/api/v1/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cache-Control"] == "no-store"
    assert "default-src 'none'" in response.headers["Content-Security-Policy"]


def test_state_changing_json_endpoint_rejects_wrong_content_type(client):
    response = client.post(
        "/api/v1/auth/register",
        data=json.dumps(_registration()),
        content_type="text/plain",
    )

    assert response.status_code == 422
    assert response.get_json()["errors"][0]["code"] == "validation_error"


def test_profile_text_rejects_invisible_control_characters(client):
    payload = _registration()
    payload["full_name"] = "Hidden\u202eName"

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422
    assert response.get_json()["errors"][0]["field"] == "full_name"


def test_request_size_limit_is_enforced():
    application = create_app(
        "testing",
        {
            "MAX_CONTENT_LENGTH": 64,
        },
    )
    with application.app_context():
        db.create_all()
    client = application.test_client()

    response = client.post("/api/v1/auth/register", json=_registration())

    assert response.status_code == 413
    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_registration_rate_limit_returns_retry_after():
    application = create_app(
        "testing",
        {
            "RATELIMIT_ENABLED": True,
            "RATELIMIT_DEFAULT": "100 per minute",
            "RATELIMIT_REGISTER": "1 per minute",
        },
    )
    with application.app_context():
        db.create_all()
    client = application.test_client()

    first = client.post("/api/v1/auth/register", json=_registration())
    second = client.post(
        "/api/v1/auth/register",
        json=_registration("security-two@example.com"),
    )

    assert first.status_code == 201
    assert second.status_code == 429
    assert second.headers["Retry-After"]
    assert second.get_json()["errors"][0]["code"] == "rate_limit_exceeded"
    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_invalid_cors_wildcard_is_rejected(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")

    with pytest.raises(RuntimeError, match="explicit HTTP"):
        create_app("testing")


def test_audit_payload_redacts_secrets_and_is_append_only(app):
    with app.test_request_context(
        "/",
        headers={"User-Agent": "Security test agent"},
    ):
        audit = record_audit(
            "security.test",
            event_data={
                "password": "never-store-this",
                "nested": {"access_token": "never-store-this-either"},
                "safe": "retained",
            },
        )
        db.session.commit()
        audit_id = audit.id

        stored = db.session.get(AuditLog, audit_id)
        assert stored.event_data["password"] == "[REDACTED]"
        assert stored.event_data["nested"]["access_token"] == "[REDACTED]"
        assert stored.event_data["safe"] == "retained"

        stored.action = "security.changed"
        with pytest.raises(RuntimeError, match="append-only"):
            db.session.commit()
        db.session.rollback()


def test_database_backup_and_restore_are_verified(tmp_path: Path):
    database = tmp_path / "live.sqlite"
    application = create_app(
        "testing",
        {"SQLALCHEMY_DATABASE_URI": f"sqlite:///{database.as_posix()}"},
    )
    with application.app_context():
        db.create_all()
        db.session.add(
            User(
                email="backup@example.com",
                full_name="Backup Patient",
                password_hash="test-only",
                role="patient",
            )
        )
        db.session.commit()
    runner = application.test_cli_runner()
    backup = tmp_path / "verified-backup.sqlite"

    created = runner.invoke(args=["database-backup", "--output", str(backup)])
    assert created.exit_code == 0, created.output

    with application.app_context():
        db.session.execute(db.delete(User))
        db.session.commit()
    restored = runner.invoke(
        args=["database-restore", str(backup), "--confirm"],
    )

    assert restored.exit_code == 0, restored.output
    with application.app_context():
        assert db.session.scalar(db.select(db.func.count(User.id))) == 1
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_privacy_maintenance_is_dry_run_by_default_and_purges_on_apply(app):
    with app.app_context():
        user = User(
            email="retention@example.com",
            full_name="Retention Patient",
            password_hash="test-only",
            role="patient",
        )
        db.session.add(user)
        db.session.flush()
        token = RefreshToken(
            user_id=user.id,
            jti_hash="a" * 64,
            family_id="retention-family",
            expires_at=datetime.now(UTC) - timedelta(days=60),
        )
        db.session.add(token)
        db.session.commit()

    runner = app.test_cli_runner()
    preview = runner.invoke(args=["privacy-maintenance"])
    assert preview.exit_code == 0
    assert '"mode": "dry_run"' in preview.output
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(RefreshToken.id))) == 1

    applied = runner.invoke(args=["privacy-maintenance", "--apply"])
    assert applied.exit_code == 0, applied.output
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(RefreshToken.id))) == 0
