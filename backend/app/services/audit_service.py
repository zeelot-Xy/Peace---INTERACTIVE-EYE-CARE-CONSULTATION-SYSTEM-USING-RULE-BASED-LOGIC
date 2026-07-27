from flask import has_request_context, request

from app.extensions import db
from app.models import AuditLog
from app.utils.security import normalize_text, sanitize_mapping


def record_audit(
    action: str,
    *,
    actor_user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    event_data: dict | None = None,
) -> AuditLog:
    user_agent = None
    if has_request_context() and request.user_agent.string:
        try:
            user_agent = normalize_text(
                request.user_agent.string,
                max_length=256,
                field_name="User agent",
            )
        except ValueError:
            user_agent = "[unsupported user agent]"
    log = AuditLog(
        action=normalize_text(action, max_length=80, field_name="Audit action"),
        actor_user_id=actor_user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        event_data=sanitize_mapping(event_data) if event_data is not None else None,
        ip_address=request.remote_addr if has_request_context() else None,
        user_agent=user_agent,
    )
    db.session.add(log)
    return log
