from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity

from app.services.audit_service import record_audit
from app.utils.responses import error_response


def role_required(role: str):
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != role:
                record_audit(
                    "auth.authorization_denied",
                    actor_user_id=get_jwt_identity(),
                    event_data={"required_role": role},
                )
                from app.extensions import db

                db.session.commit()
                return error_response(
                    "You do not have permission for this action.", 403, "forbidden"
                )
            return function(*args, **kwargs)

        return wrapped

    return decorator
