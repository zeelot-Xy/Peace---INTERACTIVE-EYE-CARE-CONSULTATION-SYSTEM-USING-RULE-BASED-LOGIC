from datetime import UTC, datetime

from flask import Blueprint
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required, unset_jwt_cookies

from app.extensions import db
from app.models import User
from app.schemas import PasswordChangeSchema, ProfileUpdateSchema
from app.services.audit_service import record_audit
from app.services.auth_service import revoke_all_sessions, revoke_token, validate_password
from app.utils.responses import error_response, success_response
from app.utils.security import normalize_text
from app.utils.validation import load_json

users_blueprint = Blueprint("users", __name__)


@users_blueprint.get("/me")
@jwt_required()
def get_profile():
    user = db.session.get(User, get_jwt_identity())
    return success_response({"user": user.to_dict()})


@users_blueprint.patch("/me")
@jwt_required()
def update_profile():
    user = db.session.get(User, get_jwt_identity())
    data = load_json(ProfileUpdateSchema())
    if "full_name" in data and data["full_name"] is not None:
        user.full_name = normalize_text(
            data["full_name"], max_length=120, field_name="Full name"
        )
    if "phone" in data:
        user.phone = (
            normalize_text(data["phone"], max_length=30, field_name="Phone") or None
            if data["phone"] is not None
            else None
        )
    if "date_of_birth" in data:
        user.date_of_birth = data["date_of_birth"]
    record_audit("profile.update", actor_user_id=user.id, resource_type="user", resource_id=user.id)
    db.session.commit()
    return success_response({"user": user.to_dict()})


@users_blueprint.post("/me/password")
@jwt_required()
def change_password():
    user = db.session.get(User, get_jwt_identity())
    data = load_json(PasswordChangeSchema())
    if not user.check_password(data["current_password"]):
        return error_response("The current password is incorrect.", 400, "invalid_current_password")
    validate_password(data["new_password"])
    if user.check_password(data["new_password"]):
        return error_response("The new password must be different.", 400, "password_unchanged")
    user.set_password(data["new_password"])
    user.password_changed_at = datetime.now(UTC)
    revoke_token(get_jwt(), "password_change")
    revoke_all_sessions(user.id, "auth.password_change")
    record_audit(
        "auth.password_change", actor_user_id=user.id, resource_type="user", resource_id=user.id
    )
    db.session.commit()
    response, status = success_response({"message": "Password changed. Please sign in again."})
    unset_jwt_cookies(response)
    return response, status
