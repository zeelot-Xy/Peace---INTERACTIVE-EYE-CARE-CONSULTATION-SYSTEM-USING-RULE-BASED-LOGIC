from flask import Blueprint
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from app.extensions import db
from app.models import User
from app.schemas import LoginSchema, RegistrationSchema
from app.services.audit_service import record_audit
from app.services.auth_service import (
    authenticate,
    issue_token_pair,
    register_user,
    revoke_all_sessions,
    revoke_token,
    revoke_token_family,
    rotate_refresh_token,
)
from app.utils.responses import success_response
from app.utils.validation import load_json

auth_blueprint = Blueprint("auth", __name__)


def _authenticated_response(user: User, access: str, refresh: str, status_code: int = 200):
    response, _ = success_response({"user": user.to_dict()}, status_code)
    set_access_cookies(response, access)
    set_refresh_cookies(response, refresh)
    return response, status_code


@auth_blueprint.post("/register")
def register():
    user = register_user(load_json(RegistrationSchema()))
    access, refresh = issue_token_pair(user)
    return _authenticated_response(user, access, refresh, 201)


@auth_blueprint.post("/login")
def login():
    data = load_json(LoginSchema())
    user = authenticate(data["email"], data["password"])
    access, refresh = issue_token_pair(user)
    return _authenticated_response(user, access, refresh)


@auth_blueprint.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = db.session.get(User, get_jwt_identity())
    access, refresh_token = rotate_refresh_token(user, get_jwt())
    return _authenticated_response(user, access, refresh_token)


@auth_blueprint.post("/logout")
@jwt_required()
def logout():
    claims = get_jwt()
    revoke_token(claims, "logout")
    revoke_token_family(claims.get("family_id"), "auth.logout")
    record_audit("auth.logout", actor_user_id=get_jwt_identity())
    db.session.commit()
    response, status = success_response({"message": "Signed out successfully."})
    unset_jwt_cookies(response)
    return response, status


@auth_blueprint.post("/logout-all")
@jwt_required()
def logout_all():
    claims = get_jwt()
    revoke_token(claims, "logout_all")
    revoke_all_sessions(get_jwt_identity())
    db.session.commit()
    response, status = success_response({"message": "All sessions have been signed out."})
    unset_jwt_cookies(response)
    return response, status
