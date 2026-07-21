from app.extensions import db
from app.models import AuditLog, RefreshToken, User


def registration_payload(**overrides):
    payload = {
        "full_name": "Test Patient",
        "email": "Patient@Example.com",
        "password": "correct horse battery staple",
    }
    payload.update(overrides)
    return payload


def register(client, **overrides):
    return client.post("/api/v1/auth/register", json=registration_payload(**overrides))


def test_registration_normalizes_email_and_sets_secure_session_cookies(app, client):
    response = register(client)

    assert response.status_code == 201
    assert response.get_json()["data"]["user"]["email"] == "patient@example.com"
    assert response.get_json()["data"]["user"]["role"] == "patient"
    assert client.get_cookie("access_token_cookie", path="/api/v1") is not None
    assert client.get_cookie("refresh_token_cookie", path="/api/v1/auth") is not None
    with app.app_context():
        user = db.session.scalar(db.select(User))
        assert user.password_hash != registration_payload()["password"]
        assert db.session.scalar(db.select(RefreshToken)) is not None


def test_registration_rejects_duplicate_and_weak_password(client):
    assert register(client).status_code == 201
    duplicate = register(client, email="PATIENT@example.com")
    weak = register(client, email="other@example.com", password="too-short")

    assert duplicate.status_code == 409
    assert weak.status_code == 422
    assert "between 12 and 128" in weak.get_json()["errors"][0]["message"]


def test_login_uses_generic_error_and_records_safe_audit(app, client, csrf_header):
    register(client)
    client.post("/api/v1/auth/logout", headers=csrf_header())
    response = client.post(
        "/api/v1/auth/login", json={"email": "patient@example.com", "password": "wrong"}
    )

    assert response.status_code == 401
    assert response.get_json()["errors"][0]["message"] == "Invalid email or password."
    with app.app_context():
        audit = db.session.scalar(
            db.select(AuditLog).where(AuditLog.action == "auth.login_failed")
        )
        assert audit is not None
        assert "wrong" not in str(audit.event_data)


def test_csrf_is_required_and_profile_can_be_updated(client, csrf_header):
    register(client)
    denied = client.patch("/api/v1/users/me", json={"full_name": "Updated Patient"})
    updated = client.patch(
        "/api/v1/users/me",
        json={"full_name": "Updated Patient", "phone": "+234 800 000 0000"},
        headers=csrf_header(),
    )

    assert denied.status_code == 401
    assert updated.status_code == 200
    assert updated.get_json()["data"]["user"]["full_name"] == "Updated Patient"


def test_refresh_rotates_token_and_rejects_reuse(app, client, csrf_header):
    register(client)
    original_refresh = client.get_cookie("refresh_token_cookie", path="/api/v1/auth").value
    original_csrf = client.get_cookie("csrf_refresh_token").value
    rotated = client.post("/api/v1/auth/refresh", headers=csrf_header("csrf_refresh_token"))

    assert rotated.status_code == 200
    assert client.get_cookie("refresh_token_cookie", path="/api/v1/auth").value != original_refresh
    with app.app_context():
        tokens = db.session.scalars(db.select(RefreshToken).order_by(RefreshToken.created_at)).all()
        assert len(tokens) == 2
        assert tokens[0].used_at is not None

    client.set_cookie("refresh_token_cookie", original_refresh, path="/api/v1/auth")
    client.set_cookie("csrf_refresh_token", original_csrf, path="/")
    replay = client.post(
        "/api/v1/auth/refresh", headers={"X-CSRF-TOKEN": original_csrf}
    )
    assert replay.status_code == 401
    with app.app_context():
        active = db.session.scalar(
            db.select(RefreshToken).where(
                RefreshToken.used_at.is_(None), RefreshToken.revoked_at.is_(None)
            )
        )
        assert active is None


def test_patient_is_forbidden_from_admin_listing(client):
    register(client)
    response = client.get("/api/v1/admin/users")

    assert response.status_code == 403
    assert response.get_json()["errors"][0]["code"] == "forbidden"


def test_administrator_can_list_safe_user_records(app, client, csrf_header):
    register(client)
    with app.app_context():
        user = db.session.scalar(db.select(User))
        user.role = "admin"
        db.session.commit()
    client.post("/api/v1/auth/logout", headers=csrf_header())
    client.post(
        "/api/v1/auth/login",
        json={
            "email": "patient@example.com",
            "password": "correct horse battery staple",
        },
    )

    response = client.get("/api/v1/admin/users")

    assert response.status_code == 200
    item = response.get_json()["data"]["items"][0]
    assert item["role"] == "admin"
    assert "password_hash" not in item


def test_admin_bootstrap_is_interactive_and_refuses_duplicates(app):
    runner = app.test_cli_runner()
    password = "a very secure admin password"
    answers = f"admin@example.com\nSystem Admin\n{password}\n{password}\n"
    created = runner.invoke(args=["bootstrap-admin"], input=answers)
    duplicate = runner.invoke(args=["bootstrap-admin"], input=answers)

    assert created.exit_code == 0
    assert "Administrator created" in created.output
    assert duplicate.exit_code != 0
    with app.app_context():
        admin = db.session.scalar(db.select(User).where(User.email == "admin@example.com"))
        assert admin.role == "admin"


def test_password_change_revokes_session(client, csrf_header):
    register(client)
    response = client.post(
        "/api/v1/users/me/password",
        json={
            "current_password": "correct horse battery staple",
            "new_password": "a completely different secure password",
        },
        headers=csrf_header(),
    )

    assert response.status_code == 200
    assert client.get_cookie("access_token_cookie", path="/api/v1") is None
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "patient@example.com", "password": "correct horse battery staple"},
    )
    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "patient@example.com",
            "password": "a completely different secure password",
        },
    )
    assert old_login.status_code == 401
    assert new_login.status_code == 200
