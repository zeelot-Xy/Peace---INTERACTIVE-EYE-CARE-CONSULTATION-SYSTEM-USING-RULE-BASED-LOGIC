from datetime import UTC, datetime
from io import BytesIO

from pypdf import PdfReader

from app.extensions import db
from app.models import AuditLog, ConsultationResponse, ConsultationSession, Report, User


def _register(client, email="adela@example.com", name="Adéla Okafor"):
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


def _csrf(client):
    cookie = client.get_cookie("csrf_access_token")
    assert cookie is not None
    return {"X-CSRF-TOKEN": cookie.value}


def _completed_consultation(app, user_id, *, long=False):
    package = app.extensions["knowledge"].get_active()
    question = package.collections["questions"][0]
    recommendations = [
        {
            "id": f"recommendation_{index}",
            "title": f"Recommended action {index}",
            "message": (
                "Arrange appropriate professional eye care and monitor any change "
                "in symptoms without delaying urgent assessment when warning signs appear."
            ),
        }
        for index in range(80 if long else 1)
    ]
    result = {
        "outcome_state": "matched",
        "completeness_state": "complete",
        "knowledge": {
            "package_id": package.package_id,
            "content_version": package.content_version,
            "fingerprint": package.fingerprint,
        },
        "overall_risk": {
            "id": "risk_routine",
            "label": "Routine eye care",
            "rank": 1,
            "action_window": "Arrange a routine eye examination.",
        },
        "matched_rules": [
            {
                "rule_id": "rule_test",
                "name": "Transparent test rule",
                "explanation": "The recorded facts matched the authored criteria.",
            }
        ],
        "possible_indications": [
            {
                "id": "condition_test",
                "possible_indication_label": "A non-diagnostic symptom pattern",
                "summary": "This pattern is for educational guidance only.",
            }
        ],
        "recommendations": recommendations,
        "red_flags": [],
        "evidence": [
            {
                "id": "source_test",
                "title": "Eye health guidance",
                "organization": "Example Public Health Body",
                "url": "https://example.org/eye-health",
            }
        ],
        "inference_trace": [],
        "disclaimer": (
            "This educational report is not a diagnosis, prescription, or replacement "
            "for an examination by a qualified eye-care professional."
        ),
        "match_score_notice": "Rule-match scores are not diagnostic probabilities.",
    }
    consultation = ConsultationSession(
        user_id=user_id,
        status="completed",
        knowledge_package_id=package.package_id,
        knowledge_version=package.content_version,
        knowledge_fingerprint=package.fingerprint,
        revision=1,
        skipped_question_ids=[],
        result_snapshot=result,
        completed_at=datetime.now(UTC),
    )
    db.session.add(consultation)
    db.session.flush()
    db.session.add(
        ConsultationResponse(
            consultation_id=consultation.id,
            question_id=question["id"],
            fact_id=question["fact_id"],
            answer={"value": 42},
        )
    )
    db.session.commit()
    return consultation.id


def test_generate_download_and_repeat_are_immutable(app, client):
    user = _register(client)
    with app.app_context():
        consultation_id = _completed_consultation(app, user["id"])

    created = client.post(
        f"/api/v1/consultations/{consultation_id}/report",
        headers=_csrf(client),
    )
    repeated = client.post(
        f"/api/v1/consultations/{consultation_id}/report",
        headers=_csrf(client),
    )

    assert created.status_code == 201
    assert repeated.status_code == 200
    metadata = created.get_json()["data"]["report"]
    assert repeated.get_json()["data"]["report"]["sha256"] == metadata["sha256"]
    download = client.get(metadata["download_url"])
    assert download.status_code == 200
    assert download.data.startswith(b"%PDF-")
    assert download.headers["Content-Type"].startswith("application/pdf")
    assert "attachment" in download.headers["Content-Disposition"]
    reader = PdfReader(BytesIO(download.data))
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert "Adéla Okafor" in text
    assert "Not provided" in text
    assert "not a diagnosis" in text.lower()
    assert "Knowledge fingerprint" in text
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Report.id))) == 1
        audit_actions = set(
            db.session.scalars(
                db.select(AuditLog.action).where(
                    AuditLog.action.in_(
                        {"report.generate", "report.download"}
                    )
                )
            )
        )
        assert audit_actions == {"report.generate", "report.download"}


def test_long_report_spans_multiple_pages(app, client):
    user = _register(client)
    with app.app_context():
        consultation_id = _completed_consultation(app, user["id"], long=True)
    created = client.post(
        f"/api/v1/consultations/{consultation_id}/report",
        headers=_csrf(client),
    )
    download = client.get(created.get_json()["data"]["report"]["download_url"])
    reader = PdfReader(BytesIO(download.data))
    ending = reader.pages[-2].extract_text() + reader.pages[-1].extract_text()

    assert len(reader.pages) >= 4
    assert "Recommended action 79" in ending


def test_report_access_is_private_but_admin_can_review(app, client):
    owner = _register(client)
    with app.app_context():
        consultation_id = _completed_consultation(app, owner["id"])
    created = client.post(
        f"/api/v1/consultations/{consultation_id}/report",
        headers=_csrf(client),
    )
    report_id = created.get_json()["data"]["report"]["id"]

    other = app.test_client()
    _register(other, "other@example.com", "Other Patient")
    assert other.get(f"/api/v1/reports/{report_id}").status_code == 404
    assert other.get(f"/api/v1/reports/{report_id}/download").status_code == 404

    admin = app.test_client()
    admin_user = _register(admin, "admin@example.com", "Report Administrator")
    with app.app_context():
        stored = db.session.get(User, admin_user["id"])
        stored.role = "admin"
        db.session.commit()
    admin.post(
        "/api/v1/auth/logout",
        headers={
            "X-CSRF-TOKEN": admin.get_cookie("csrf_access_token").value
        },
    )
    login = admin.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "correct horse battery staple",
        },
    )
    assert login.status_code == 200
    assert admin.get(f"/api/v1/reports/{report_id}").status_code == 200
    assert admin.get(f"/api/v1/reports/{report_id}/download").status_code == 200


def test_report_requires_completed_owned_consultation(app, client):
    user = _register(client)
    package = app.extensions["knowledge"].get_active()
    with app.app_context():
        consultation = ConsultationSession(
            user_id=user["id"],
            status="in_progress",
            knowledge_package_id=package.package_id,
            knowledge_version=package.content_version,
            knowledge_fingerprint=package.fingerprint,
            skipped_question_ids=[],
        )
        db.session.add(consultation)
        db.session.commit()
        consultation_id = consultation.id

    response = client.post(
        f"/api/v1/consultations/{consultation_id}/report",
        headers=_csrf(client),
    )
    assert response.status_code == 409
    assert response.get_json()["errors"][0]["code"] == "invalid_consultation_state"


def test_history_filters_and_exposes_existing_report(app, client):
    user = _register(client)
    with app.app_context():
        consultation_id = _completed_consultation(app, user["id"])
    report = client.post(
        f"/api/v1/consultations/{consultation_id}/report",
        headers=_csrf(client),
    ).get_json()["data"]["report"]

    matched = client.get(
        "/api/v1/consultations?status=completed&risk=risk_routine"
    )
    excluded = client.get("/api/v1/consultations?status=cancelled")
    invalid = client.get("/api/v1/consultations?date_from=2026-99-99")

    item = matched.get_json()["data"]["items"][0]
    assert item["id"] == consultation_id
    assert item["report_id"] == report["id"]
    assert excluded.get_json()["data"]["items"] == []
    assert invalid.status_code == 422
