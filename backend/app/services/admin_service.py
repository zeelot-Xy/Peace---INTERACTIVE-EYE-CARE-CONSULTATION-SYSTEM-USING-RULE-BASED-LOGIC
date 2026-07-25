"""Read-only administrator reporting over application persistence."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func

from app.extensions import db
from app.models import AuditLog, ConsultationSession, Report, User


def _pagination(result) -> dict[str, int]:
    return {
        "page": result.page,
        "per_page": result.per_page,
        "pages": result.pages,
        "total": result.total,
    }


def get_summary() -> dict[str, Any]:
    user_counts = dict(
        db.session.execute(
            db.select(User.role, func.count(User.id)).group_by(User.role)
        ).all()
    )
    consultation_counts = dict(
        db.session.execute(
            db.select(ConsultationSession.status, func.count(ConsultationSession.id)).group_by(
                ConsultationSession.status
            )
        ).all()
    )
    return {
        "users": {
            "total": sum(user_counts.values()),
            "patients": user_counts.get("patient", 0),
            "administrators": user_counts.get("admin", 0),
        },
        "consultations": {
            "total": sum(consultation_counts.values()),
            "in_progress": consultation_counts.get("in_progress", 0),
            "completed": consultation_counts.get("completed", 0),
            "cancelled": consultation_counts.get("cancelled", 0),
        },
        "reports": db.session.scalar(db.select(func.count(Report.id))) or 0,
    }


def list_consultations(*, page: int, per_page: int) -> dict[str, Any]:
    result = db.paginate(
        db.select(ConsultationSession).order_by(ConsultationSession.created_at.desc()),
        page=page,
        per_page=per_page,
        max_per_page=100,
        error_out=False,
    )
    return {
        "items": [
            {
                "id": session.id,
                "patient": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                },
                "status": session.status,
                "knowledge_version": session.knowledge_version,
                "knowledge_fingerprint": session.knowledge_fingerprint,
                "risk": (
                    session.result_snapshot.get("overall_risk")
                    if session.result_snapshot
                    else None
                ),
                "created_at": session.created_at.isoformat(),
                "completed_at": (
                    session.completed_at.isoformat() if session.completed_at else None
                ),
            }
            for session in result.items
            for user in (session.user,)
        ],
        "pagination": _pagination(result),
    }


def get_consultation_report(consultation_id: str) -> dict[str, Any] | None:
    row = db.session.execute(
        db.select(ConsultationSession, User)
        .join(User, User.id == ConsultationSession.user_id)
        .where(ConsultationSession.id == consultation_id)
    ).first()
    if row is None:
        return None
    session, user = row
    return {
        "consultation_id": session.id,
        "patient": user.to_dict(),
        "status": session.status,
        "knowledge": {
            "package_id": session.knowledge_package_id,
            "content_version": session.knowledge_version,
            "fingerprint": session.knowledge_fingerprint,
        },
        "result": session.result_snapshot,
        "created_at": session.created_at.isoformat(),
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }


def list_audit_logs(*, page: int, per_page: int) -> dict[str, Any]:
    result = db.paginate(
        db.select(AuditLog).order_by(AuditLog.created_at.desc()),
        page=page,
        per_page=per_page,
        max_per_page=100,
        error_out=False,
    )
    actor_ids = {item.actor_user_id for item in result.items if item.actor_user_id}
    actors = {
        user.id: user
        for user in db.session.scalars(
            db.select(User).where(User.id.in_(actor_ids))
        ).all()
    }
    return {
        "items": [
            {
                "id": audit.id,
                "action": audit.action,
                "actor": (
                    {
                        "id": actors[audit.actor_user_id].id,
                        "full_name": actors[audit.actor_user_id].full_name,
                        "email": actors[audit.actor_user_id].email,
                    }
                    if audit.actor_user_id in actors
                    else None
                ),
                "resource_type": audit.resource_type,
                "resource_id": audit.resource_id,
                "event_data": audit.event_data,
                "created_at": audit.created_at.isoformat(),
            }
            for audit in result.items
        ],
        "pagination": _pagination(result),
    }
