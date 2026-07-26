"""Cross-layer verification scenarios used for the project defence."""

from io import BytesIO

from pypdf import PdfReader

from app.extensions import db
from app.models import AuditLog, User


def _register(client, email: str, name: str = "Defence Demo Patient"):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": name,
            "email": email,
            "password": "correct horse battery staple",
        },
    )
    assert response.status_code == 201
    return response.get_json()["data"]["user"]


def _csrf(client) -> dict[str, str]:
    cookie = client.get_cookie("csrf_access_token")
    assert cookie is not None
    return {"X-CSRF-TOKEN": cookie.value}


def _answer_for(question, package):
    fact = package.indexes["symptoms"][question["fact_id"]]
    if question["id"] == "question_chemical_exposure":
        return True
    if fact["value_type"] == "boolean":
        return False
    if fact["value_type"] == "integer":
        return max(fact["minimum"], 35)
    return fact["allowed_values"][0]


def test_patient_defence_journey_from_registration_to_immutable_report(app, client):
    patient = _register(client, "defence.patient@example.com", "Adéla Okafor")
    created = client.post("/api/v1/consultations", headers=_csrf(client))
    assert created.status_code == 201
    consultation = created.get_json()["data"]["consultation"]
    package = app.extensions["knowledge"].get_active()
    answered_ids: list[str] = []

    while consultation["next_question"] is not None:
        question = consultation["next_question"]
        response = client.put(
            (
                f"/api/v1/consultations/{consultation['id']}/responses/"
                f"{question['id']}"
            ),
            json={
                "answer": _answer_for(question, package),
                "skip": False,
                "revision": consultation["revision"],
            },
            headers=_csrf(client),
        )
        assert response.status_code == 200
        answered_ids.append(question["id"])
        consultation = response.get_json()["data"]["consultation"]
        assert len(answered_ids) <= len(package.collections["questions"])

    assert "question_chemical_exposure" in answered_ids
    completed = client.post(
        f"/api/v1/consultations/{consultation['id']}/complete",
        json={"revision": consultation["revision"]},
        headers=_csrf(client),
    )
    assert completed.status_code == 200
    result = completed.get_json()["data"]["result"]
    assert result["overall_risk"]["id"] == "risk_emergency"
    assert result["red_flags"]
    assert result["matched_rules"]
    assert result["inference_trace"]
    assert result["knowledge"]["fingerprint"] == package.fingerprint
    assert "not a diagnosis" in result["disclaimer"].lower()

    generated = client.post(
        f"/api/v1/consultations/{consultation['id']}/report",
        headers=_csrf(client),
    )
    assert generated.status_code == 201
    report = generated.get_json()["data"]["report"]
    download = client.get(report["download_url"])
    assert download.status_code == 200
    assert download.headers["Cache-Control"] == "private, no-store"
    assert download.headers["X-Content-Type-Options"] == "nosniff"
    pdf_text = "\n".join(
        page.extract_text() for page in PdfReader(BytesIO(download.data)).pages
    )
    assert "Adéla Okafor" in pdf_text
    assert "Emergency" in pdf_text
    assert "not a diagnosis" in pdf_text.lower()

    history = client.get(
        "/api/v1/consultations?status=completed&risk=risk_emergency"
    )
    item = history.get_json()["data"]["items"][0]
    assert item["id"] == consultation["id"]
    assert item["report_id"] == report["id"]
    assert item["knowledge_version"] == package.content_version

    other = app.test_client()
    _register(other, "defence.other@example.com", "Other Demo Patient")
    assert other.get(report["download_url"]).status_code == 404

    with app.app_context():
        audit_actions = set(
            db.session.scalars(
                db.select(AuditLog.action).where(
                    AuditLog.actor_user_id == patient["id"]
                )
            )
        )
    assert {
        "consultation.create",
        "consultation.answer_saved",
        "consultation.complete",
        "report.generate",
        "report.download",
    } <= audit_actions


def test_administrator_can_review_but_patient_cannot_cross_role_boundary(
    app, client
):
    patient = _register(client, "role.patient@example.com")
    assert client.get("/api/v1/admin/summary").status_code == 403
    assert client.get("/api/v1/admin/audit-logs").status_code == 403

    admin = app.test_client()
    administrator = _register(
        admin, "role.admin@example.com", "Defence Administrator"
    )
    with app.app_context():
        stored = db.session.get(User, administrator["id"])
        stored.role = "admin"
        db.session.commit()
    assert (
        admin.post("/api/v1/auth/logout", headers=_csrf(admin)).status_code
        == 200
    )
    login = admin.post(
        "/api/v1/auth/login",
        json={
            "email": "role.admin@example.com",
            "password": "correct horse battery staple",
        },
    )
    assert login.status_code == 200

    summary = admin.get("/api/v1/admin/summary")
    users = admin.get("/api/v1/admin/users?per_page=10")
    audits = admin.get("/api/v1/admin/audit-logs?per_page=20")
    assert summary.status_code == 200
    assert summary.get_json()["data"]["summary"]["users"]["total"] == 2
    assert users.status_code == 200
    assert {item["id"] for item in users.get_json()["data"]["items"]} == {
        patient["id"],
        administrator["id"],
    }
    audit_body = audits.get_json()
    assert audits.status_code == 200
    assert "password" not in str(audit_body).lower()
    assert "correct horse battery staple" not in str(audit_body)


def test_security_negative_api_contracts_are_stable(client):
    unauthenticated = client.get("/api/v1/reports")
    assert unauthenticated.status_code == 401
    assert unauthenticated.get_json()["correlation_id"]

    _register(client, "negative.contracts@example.com")
    missing_csrf = client.post("/api/v1/consultations")
    invalid_pagination = client.get("/api/v1/reports?page=not-a-number")
    invalid_history_range = client.get(
        "/api/v1/consultations?date_from=2026-07-20&date_to=2026-07-01"
    )

    assert missing_csrf.status_code == 401
    assert (
        missing_csrf.get_json()["errors"][0]["code"]
        == "authentication_required"
    )
    assert invalid_pagination.status_code == 422
    assert invalid_pagination.get_json()["errors"][0]["code"] == "validation_error"
    assert invalid_history_range.status_code == 422
    for response in (
        missing_csrf,
        invalid_pagination,
        invalid_history_range,
    ):
        body = response.get_json()
        assert set(body) == {"correlation_id", "data", "errors"}
        assert body["data"] is None
        assert body["correlation_id"]
