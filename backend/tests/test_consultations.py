from dataclasses import replace
from types import MappingProxyType, SimpleNamespace

from app.extensions import db
from app.knowledge.contracts import freeze
from app.models import AuditLog, ConsultationResponse, ConsultationSession
from app.services.consultation_service import _eligible_questions


def _register(client, email="patient@example.com"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Consultation Patient",
            "email": email,
            "password": "correct horse battery staple",
        },
    )


def _csrf(client):
    cookie = client.get_cookie("csrf_access_token")
    assert cookie is not None
    return {"X-CSRF-TOKEN": cookie.value}


def _create(client):
    response = client.post("/api/v1/consultations", headers=_csrf(client))
    assert response.status_code == 201
    return response.get_json()["data"]["consultation"]


def _answer(client, session, question_id, answer=None, skip=False):
    response = client.put(
        f"/api/v1/consultations/{session['id']}/responses/{question_id}",
        json={"answer": answer, "skip": skip, "revision": session["revision"]},
        headers=_csrf(client),
    )
    if response.status_code == 200:
        return response.get_json()["data"]["consultation"]
    return response


def _valid_value(question, package):
    definition = package.indexes["symptoms"][question["fact_id"]]
    if definition["value_type"] == "boolean":
        return False
    if definition["value_type"] == "integer":
        return definition["minimum"]
    return definition["allowed_values"][0]


def test_create_freezes_knowledge_and_returns_first_question(app, client):
    _register(client)

    session = _create(client)

    package = app.extensions["knowledge"].get_active()
    assert session["status"] == "in_progress"
    assert session["revision"] == 0
    assert session["knowledge"]["fingerprint"] == package.fingerprint
    assert session["next_question"]["id"] == "question_age_years"
    assert session["progress"]["percentage"] == 0.0
    with app.app_context():
        stored = db.session.get(ConsultationSession, session["id"])
        assert stored.knowledge_package_id == package.package_id


def test_answer_autosaves_resumes_and_can_be_revised(app, client):
    _register(client)
    session = _create(client)

    session = _answer(client, session, "question_age_years", 40)
    assert session["revision"] == 1
    assert session["next_question"]["id"] == "question_sudden_vision_loss"
    resumed = client.get(f"/api/v1/consultations/{session['id']}")
    saved_answer = resumed.get_json()["data"]["consultation"]["answers"][0]
    assert saved_answer["answer"] == 40
    assert saved_answer["question"]["prompt"] == "What is your age in completed years?"
    assert saved_answer["question"]["citation_ids"]

    session = _answer(client, session, "question_age_years", 41)
    assert session["revision"] == 2
    assert session["answers"][0]["answer"] == 41
    with app.app_context():
        count = db.session.scalar(
            db.select(db.func.count(ConsultationResponse.id))
        )
        assert count == 1
        audit = db.session.scalar(
            db.select(AuditLog)
            .where(AuditLog.action == "consultation.answer_saved")
            .order_by(AuditLog.created_at.desc())
        )
        assert audit.event_data["question_id"] == "question_age_years"
        assert "41" not in str(audit.event_data)


def test_invalid_answer_and_stale_revision_are_rejected(client):
    _register(client)
    session = _create(client)

    invalid = _answer(client, session, "question_age_years", 10)
    assert invalid.status_code == 422
    assert invalid.get_json()["errors"][0]["code"] == "invalid_consultation_answer"

    saved = _answer(client, session, "question_age_years", 30)
    stale = client.put(
        f"/api/v1/consultations/{session['id']}/responses/question_redness",
        json={"answer": True, "revision": 0},
        headers=_csrf(client),
    )
    assert saved["revision"] == 1
    assert stale.status_code == 409
    assert stale.get_json()["errors"][0]["code"] == "consultation_revision_conflict"


def test_partial_emergency_answer_surfaces_immediate_safety_alert(client):
    _register(client)
    session = _create(client)

    session = _answer(client, session, "question_chemical_exposure", True)

    assert session["safety_alert"]["requires_immediate_action"] is True
    assert session["safety_alert"]["risk"]["id"] == "risk_emergency"
    assert session["status"] == "in_progress"


def test_required_safety_question_cannot_be_skipped(client):
    _register(client)
    session = _create(client)

    response = _answer(
        client, session, "question_chemical_exposure", answer=None, skip=True
    )

    assert response.status_code == 422
    assert "cannot be skipped" in response.get_json()["errors"][0]["message"]


def test_optional_question_can_be_skipped_with_custom_frozen_package(app, client):
    manager = app.extensions["knowledge"]
    original = manager.get_active()
    questions = list(original.collections["questions"])
    position = next(
        index
        for index, question in enumerate(questions)
        if question["id"] == "question_screen_related"
    )
    authored = dict(questions[position])
    authored["required"] = False
    optional = freeze(authored)
    questions[position] = optional
    collections = dict(original.collections)
    collections["questions"] = tuple(questions)
    indexes = dict(original.indexes)
    question_index = dict(indexes["questions"])
    question_index[optional["id"]] = optional
    indexes["questions"] = MappingProxyType(question_index)
    manager._active = replace(
        original,
        fingerprint="optional-question-test-fingerprint",
        collections=MappingProxyType(collections),
        indexes=MappingProxyType(indexes),
    )
    _register(client)
    session = _create(client)

    session = _answer(
        client, session, "question_screen_related", answer=None, skip=True
    )

    assert session["skipped_question_ids"] == ["question_screen_related"]


def test_conditional_branching_never_hides_safety_questions():
    base = {
        "id": "question_branch",
        "safety_critical": False,
        "show_when": {
            "fact_id": "fact_redness",
            "operator": "eq",
            "value": True,
        },
    }
    safety = {**base, "id": "question_safety", "safety_critical": True}
    package = SimpleNamespace(collections={"questions": (base, safety)})

    false_branch = _eligible_questions(package, {"fact_redness": False})
    true_branch = _eligible_questions(package, {"fact_redness": True})

    assert [item["id"] for item in false_branch] == ["question_safety"]
    assert [item["id"] for item in true_branch] == [
        "question_branch",
        "question_safety",
    ]


def test_clear_answer_supports_back_navigation(client):
    _register(client)
    session = _create(client)
    session = _answer(client, session, "question_age_years", 35)

    response = client.delete(
        f"/api/v1/consultations/{session['id']}/responses/question_age_years",
        json={"revision": session["revision"]},
        headers=_csrf(client),
    )

    assert response.status_code == 200
    state = response.get_json()["data"]["consultation"]
    assert state["answers"] == []
    assert state["next_question"]["id"] == "question_age_years"


def test_completion_requires_all_applicable_questions(client):
    _register(client)
    session = _create(client)

    response = client.post(
        f"/api/v1/consultations/{session['id']}/complete",
        json={"revision": session["revision"]},
        headers=_csrf(client),
    )

    assert response.status_code == 409
    assert "incomplete" in response.get_json()["errors"][0]["message"].lower()


def test_full_completion_persists_reproducible_result_and_history(app, client):
    _register(client)
    session = _create(client)
    package = app.extensions["knowledge"].get_active()
    for question in package.collections["questions"]:
        session = _answer(
            client, session, question["id"], _valid_value(question, package)
        )

    completed = client.post(
        f"/api/v1/consultations/{session['id']}/complete",
        json={"revision": session["revision"]},
        headers=_csrf(client),
    )

    assert completed.status_code == 200
    payload = completed.get_json()["data"]
    assert payload["consultation"]["status"] == "completed"
    assert payload["result"]["knowledge"]["fingerprint"] == package.fingerprint
    result = client.get(f"/api/v1/consultations/{session['id']}/result")
    assert result.get_json()["data"]["result"] == payload["result"]
    history = client.get("/api/v1/consultations")
    assert history.get_json()["data"]["items"][0]["status"] == "completed"
    with app.app_context():
        audit = db.session.scalar(
            db.select(AuditLog).where(AuditLog.action == "consultation.complete")
        )
        assert audit.event_data["knowledge_fingerprint"] == package.fingerprint


def test_cancelled_consultation_cannot_be_modified(client):
    _register(client)
    session = _create(client)
    cancelled = client.post(
        f"/api/v1/consultations/{session['id']}/cancel",
        json={"revision": session["revision"]},
        headers=_csrf(client),
    )
    state = cancelled.get_json()["data"]["consultation"]

    response = _answer(client, state, "question_age_years", 30)

    assert state["status"] == "cancelled"
    assert response.status_code == 409


def test_consultations_are_private_to_their_owner(app, client):
    _register(client)
    session = _create(client)
    other = app.test_client()
    _register(other, "other@example.com")

    response = other.get(f"/api/v1/consultations/{session['id']}")

    assert response.status_code == 404


def test_authentication_and_csrf_are_required(client):
    unauthenticated = client.post("/api/v1/consultations")
    assert unauthenticated.status_code == 401
    _register(client)

    missing_csrf = client.post("/api/v1/consultations")

    assert missing_csrf.status_code == 401
