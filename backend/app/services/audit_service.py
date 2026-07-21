from flask import has_request_context, request

from app.extensions import db
from app.models import AuditLog


def record_audit(
    action: str,
    *,
    actor_user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    event_data: dict | None = None,
) -> AuditLog:
    log = AuditLog(
        action=action,
        actor_user_id=actor_user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        event_data=event_data,
        ip_address=request.remote_addr if has_request_context() else None,
        user_agent=(request.user_agent.string[:256] if has_request_context() else None),
    )
    db.session.add(log)
    return log
