"""Consultation lifecycle orchestration over immutable knowledge snapshots."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

from flask import current_app

from app.extensions import db
from app.inference import FactValidationError, TruthValue, evaluate_expression, normalize_facts
from app.knowledge import KnowledgeLoadError, KnowledgePackage
from app.models import ConsultationResponse, ConsultationSession, Report
from app.services.audit_service import record_audit


class ConsultationError(RuntimeError):
    code = "consultation_error"
    status_code = 400


class ConsultationNotFound(ConsultationError):
    code = "consultation_not_found"
    status_code = 404


class ConsultationConflict(ConsultationError):
    code = "consultation_revision_conflict"
    status_code = 409


class ConsultationStateError(ConsultationError):
    code = "invalid_consultation_state"
    status_code = 409


class ConsultationInputError(ConsultationError):
    code = "invalid_consultation_answer"
    status_code = 422


def _get_session(user_id: str, consultation_id: str) -> ConsultationSession:
    session = db.session.scalar(
        db.select(ConsultationSession).where(
            ConsultationSession.id == consultation_id,
            ConsultationSession.user_id == user_id,
        )
    )
    if session is None:
        raise ConsultationNotFound("Consultation was not found.")
    return session


def _package_for(session: ConsultationSession) -> KnowledgePackage:
    manager = current_app.extensions["knowledge"]
    active = manager.get_active()
    if active.fingerprint == session.knowledge_fingerprint:
        return active
    if not session.knowledge_package_id:
        raise ConsultationStateError("Consultation has no frozen knowledge package.")
    package_path = (
        Path(current_app.config["KNOWLEDGE_PACKAGES_DIR"])
        / session.knowledge_package_id
    )
    try:
        package = manager.load(package_path)
    except KnowledgeLoadError as error:
        raise ConsultationStateError(
            "The consultation's frozen knowledge package is unavailable."
        ) from error
    if package.fingerprint != session.knowledge_fingerprint:
        raise ConsultationStateError(
            "The consultation's frozen knowledge package no longer matches its fingerprint."
        )
    return package


def _answers(session: ConsultationSession, package: KnowledgePackage) -> dict[str, Any]:
    questions = package.indexes["questions"]
    return {
        questions[response.question_id]["fact_id"]: response.answer["value"]
        for response in session.responses
        if response.question_id in questions
    }


def _response_index(
    session: ConsultationSession,
) -> dict[str, ConsultationResponse]:
    return {response.question_id: response for response in session.responses}


def _eligible_questions(
    package: KnowledgePackage, facts: dict[str, Any]
) -> tuple[dict[str, Any], ...]:
    eligible = []
    for question in package.collections["questions"]:
        if question["safety_critical"] or "show_when" not in question:
            eligible.append(question)
            continue
        branch = evaluate_expression(question["show_when"], facts)
        if branch.truth is TruthValue.TRUE:
            eligible.append(question)
    return tuple(eligible)


def _question_payload(question: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": question["id"],
        "fact_id": question["fact_id"],
        "prompt": question["prompt"],
        "help_text": question.get("help_text"),
        "answer_type": question["answer_type"],
        "required": question["required"],
        "safety_critical": question["safety_critical"],
        "options": [dict(option) for option in question.get("options", ())],
        "citation_ids": list(question["citation_ids"]),
    }


def _safety_alert(package: KnowledgePackage, facts: dict[str, Any]) -> dict[str, Any] | None:
    if not facts:
        return None
    result = current_app.extensions["inference"].evaluate(package, facts)
    if not result.overall_risk or result.overall_risk["rank"] < 3:
        return None
    return {
        "requires_immediate_action": True,
        "risk": dict(result.overall_risk),
        "red_flags": [dict(item) for item in result.red_flags],
        "recommendations": [dict(item) for item in result.recommendations],
        "disclaimer": result.disclaimer,
    }


def _state(session: ConsultationSession, package: KnowledgePackage) -> dict[str, Any]:
    facts = _answers(session, package)
    eligible = _eligible_questions(package, facts)
    responses = _response_index(session)
    skipped = set(session.skipped_question_ids or ())
    unresolved = [
        question
        for question in eligible
        if question["id"] not in responses and question["id"] not in skipped
    ]
    resolved_count = len(eligible) - len(unresolved)
    percentage = round((resolved_count / len(eligible)) * 100, 2) if eligible else 100.0
    answer_items = [
        {
            "question_id": response.question_id,
            "fact_id": response.fact_id,
            "answer": response.answer["value"],
            "question": _question_payload(
                package.indexes["questions"][response.question_id]
            ),
        }
        for response in sorted(session.responses, key=lambda item: item.question_id)
    ]
    return {
        "id": session.id,
        "status": session.status,
        "revision": session.revision,
        "knowledge": {
            "package_id": session.knowledge_package_id,
            "content_version": session.knowledge_version,
            "fingerprint": session.knowledge_fingerprint,
        },
        "progress": {
            "resolved": resolved_count,
            "total_applicable": len(eligible),
            "percentage": percentage,
        },
        "next_question": _question_payload(unresolved[0]) if unresolved else None,
        "answers": answer_items,
        "skipped_question_ids": sorted(skipped),
        "safety_alert": _safety_alert(package, facts),
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        "cancelled_at": session.cancelled_at.isoformat() if session.cancelled_at else None,
    }


def _advance_revision(
    session: ConsultationSession, expected_revision: int
) -> None:
    result = db.session.execute(
        db.update(ConsultationSession)
        .where(
            ConsultationSession.id == session.id,
            ConsultationSession.revision == expected_revision,
        )
        .values(revision=ConsultationSession.revision + 1)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        db.session.rollback()
        current_revision = db.session.scalar(
            db.select(ConsultationSession.revision).where(
                ConsultationSession.id == session.id
            )
        )
        raise ConsultationConflict(
            f"Consultation changed; expected revision {expected_revision}, "
            f"current revision is {current_revision}."
        )
    db.session.refresh(session)


def _check_editable(session: ConsultationSession) -> None:
    if session.status != "in_progress":
        raise ConsultationStateError(
            f"Consultation cannot be changed while status is '{session.status}'."
        )


def create_consultation(user_id: str) -> dict[str, Any]:
    package = current_app.extensions["knowledge"].get_active()
    session = ConsultationSession(
        user_id=user_id,
        status="in_progress",
        knowledge_package_id=package.package_id,
        knowledge_version=package.content_version,
        knowledge_fingerprint=package.fingerprint,
        revision=0,
        skipped_question_ids=[],
    )
    db.session.add(session)
    db.session.flush()
    record_audit(
        "consultation.create",
        actor_user_id=user_id,
        resource_type="consultation",
        resource_id=session.id,
        event_data={"knowledge_fingerprint": package.fingerprint},
    )
    db.session.commit()
    return _state(session, package)


def get_consultation(user_id: str, consultation_id: str) -> dict[str, Any]:
    session = _get_session(user_id, consultation_id)
    return _state(session, _package_for(session))


def save_answer(
    user_id: str,
    consultation_id: str,
    question_id: str,
    *,
    answer: Any,
    skip: bool,
    expected_revision: int,
) -> dict[str, Any]:
    session = _get_session(user_id, consultation_id)
    _check_editable(session)
    package = _package_for(session)
    question = package.indexes["questions"].get(question_id)
    if question is None:
        raise ConsultationInputError("Question is not part of the frozen knowledge package.")
    facts = _answers(session, package)
    if question not in _eligible_questions(package, facts):
        raise ConsultationInputError("Question is not currently applicable.")
    responses = _response_index(session)
    skipped = set(session.skipped_question_ids or ())
    if skip:
        if question["required"] or question["safety_critical"]:
            raise ConsultationInputError("This required question cannot be skipped.")
        _advance_revision(session, expected_revision)
        if existing := responses.get(question_id):
            db.session.delete(existing)
        skipped.add(question_id)
    else:
        try:
            normalize_facts(package, {question["fact_id"]: answer})
        except FactValidationError as error:
            message = error.issues[0].message if error.issues else "Answer is invalid."
            raise ConsultationInputError(message) from error
        _advance_revision(session, expected_revision)
        skipped.discard(question_id)
        response = responses.get(question_id)
        if response is None:
            response = ConsultationResponse(
                consultation=session,
                question_id=question_id,
                fact_id=question["fact_id"],
                answer={"value": answer},
            )
            db.session.add(response)
        else:
            response.fact_id = question["fact_id"]
            response.answer = {"value": answer}
    session.skipped_question_ids = sorted(skipped)
    db.session.flush()
    _remove_inapplicable_responses(session, package)
    record_audit(
        "consultation.answer_saved",
        actor_user_id=user_id,
        resource_type="consultation",
        resource_id=session.id,
        event_data={
            "question_id": question_id,
            "skipped": skip,
            "revision": session.revision,
        },
    )
    db.session.commit()
    return _state(session, package)


def _remove_inapplicable_responses(
    session: ConsultationSession, package: KnowledgePackage
) -> None:
    facts = _answers(session, package)
    eligible_ids = {
        question["id"] for question in _eligible_questions(package, facts)
    }
    removed = False
    for response in tuple(session.responses):
        if response.question_id not in eligible_ids:
            db.session.delete(response)
            removed = True
    skipped = set(session.skipped_question_ids or ())
    next_skipped = sorted(skipped & eligible_ids)
    if next_skipped != sorted(skipped):
        session.skipped_question_ids = next_skipped
        removed = True
    if removed:
        session.revision += 1
        db.session.flush()


def clear_answer(
    user_id: str,
    consultation_id: str,
    question_id: str,
    expected_revision: int,
) -> dict[str, Any]:
    session = _get_session(user_id, consultation_id)
    _check_editable(session)
    package = _package_for(session)
    if question_id not in package.indexes["questions"]:
        raise ConsultationInputError("Question is not part of the frozen knowledge package.")
    response = _response_index(session).get(question_id)
    skipped = set(session.skipped_question_ids or ())
    if response is None and question_id not in skipped:
        raise ConsultationInputError("Question has no saved answer or skip.")
    _advance_revision(session, expected_revision)
    if response is not None:
        db.session.delete(response)
    skipped.discard(question_id)
    session.skipped_question_ids = sorted(skipped)
    record_audit(
        "consultation.answer_cleared",
        actor_user_id=user_id,
        resource_type="consultation",
        resource_id=session.id,
        event_data={"question_id": question_id, "revision": session.revision},
    )
    db.session.commit()
    return _state(session, package)


def complete_consultation(
    user_id: str, consultation_id: str, expected_revision: int
) -> dict[str, Any]:
    session = _get_session(user_id, consultation_id)
    _check_editable(session)
    package = _package_for(session)
    facts = _answers(session, package)
    responses = _response_index(session)
    skipped = set(session.skipped_question_ids or ())
    unresolved = [
        question["id"]
        for question in _eligible_questions(package, facts)
        if question["id"] not in responses and question["id"] not in skipped
    ]
    if unresolved:
        raise ConsultationStateError(
            f"Consultation is incomplete; {len(unresolved)} applicable question(s) remain."
        )
    result = current_app.extensions["inference"].evaluate(package, facts).to_dict()
    _advance_revision(session, expected_revision)
    session.status = "completed"
    session.completed_at = datetime.now(UTC)
    session.result_snapshot = result
    record_audit(
        "consultation.complete",
        actor_user_id=user_id,
        resource_type="consultation",
        resource_id=session.id,
        event_data={
            "knowledge_fingerprint": package.fingerprint,
            "risk_id": result["overall_risk"]["id"] if result["overall_risk"] else None,
        },
    )
    db.session.commit()
    return {"consultation": _state(session, package), "result": result}


def cancel_consultation(
    user_id: str, consultation_id: str, expected_revision: int
) -> dict[str, Any]:
    session = _get_session(user_id, consultation_id)
    _check_editable(session)
    _advance_revision(session, expected_revision)
    package = _package_for(session)
    session.status = "cancelled"
    session.cancelled_at = datetime.now(UTC)
    record_audit(
        "consultation.cancel",
        actor_user_id=user_id,
        resource_type="consultation",
        resource_id=session.id,
    )
    db.session.commit()
    return _state(session, package)


def get_result(user_id: str, consultation_id: str) -> dict[str, Any]:
    session = _get_session(user_id, consultation_id)
    if session.status != "completed" or session.result_snapshot is None:
        raise ConsultationStateError("Consultation has no completed result.")
    return session.result_snapshot


def list_consultations(
    user_id: str,
    *,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    risk_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[str, Any]:
    statement = db.select(ConsultationSession).where(
        ConsultationSession.user_id == user_id
    )
    if status:
        if status not in {"in_progress", "completed", "cancelled"}:
            raise ConsultationInputError("Status filter is invalid.")
        statement = statement.where(ConsultationSession.status == status)
    if risk_id:
        valid_risks = current_app.extensions["knowledge"].get_active().indexes[
            "risk_levels"
        ]
        if risk_id not in valid_risks:
            raise ConsultationInputError("Risk filter is invalid.")
        statement = statement.where(
            db.func.json_extract(
                ConsultationSession.result_snapshot, "$.overall_risk.id"
            )
            == risk_id
        )
    if date_from:
        statement = statement.where(
            ConsultationSession.created_at
            >= datetime.combine(date_from, time.min, tzinfo=UTC)
        )
    if date_to:
        statement = statement.where(
            ConsultationSession.created_at
            < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=UTC)
        )
    pagination = db.paginate(
        statement.order_by(
            ConsultationSession.created_at.desc(), ConsultationSession.id
        ),
        page=page,
        per_page=per_page,
        max_per_page=50,
        error_out=False,
    )
    report_by_consultation = {
        report.consultation_id: report.id
        for report in db.session.scalars(
            db.select(Report).where(
                Report.consultation_id.in_(
                    [session.id for session in pagination.items]
                )
            )
        )
    }
    return {
        "items": [
            {
                "id": session.id,
                "status": session.status,
                "revision": session.revision,
                "knowledge_version": session.knowledge_version,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "completed_at": (
                    session.completed_at.isoformat() if session.completed_at else None
                ),
                "cancelled_at": (
                    session.cancelled_at.isoformat() if session.cancelled_at else None
                ),
                "risk": (
                    session.result_snapshot.get("overall_risk")
                    if session.result_snapshot
                    else None
                ),
                "report_id": report_by_consultation.get(session.id),
            }
            for session in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }
