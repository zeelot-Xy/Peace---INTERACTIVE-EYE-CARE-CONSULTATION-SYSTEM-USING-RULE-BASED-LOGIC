import hashlib
import uuid
from datetime import UTC, datetime
from typing import Any

from flask import current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

from app.extensions import db
from app.models import RefreshToken, TokenRevocation, User
from app.services.audit_service import record_audit
from app.utils.security import normalize_text


class AuthenticationError(Exception):
    pass


class ConflictError(Exception):
    pass


class PasswordPolicyError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def validate_password(password: str) -> None:
    minimum = current_app.config["PASSWORD_MIN_LENGTH"]
    maximum = current_app.config["PASSWORD_MAX_LENGTH"]
    if not minimum <= len(password) <= maximum:
        raise PasswordPolicyError(
            f"Password must be between {minimum} and {maximum} characters."
        )


def _hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


def _request_metadata() -> tuple[str | None, str | None]:
    return request.remote_addr, request.user_agent.string[:256]


def register_user(data: dict[str, Any]) -> User:
    email = normalize_email(data["email"])
    if db.session.scalar(db.select(User).where(User.email == email)):
        raise ConflictError("An account could not be created with those details.")
    validate_password(data["password"])
    full_name = normalize_text(data["full_name"], max_length=120, field_name="Full name")
    user = User(email=email, full_name=full_name, role="patient")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()
    record_audit("auth.register", actor_user_id=user.id, resource_type="user", resource_id=user.id)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User:
    user = db.session.scalar(db.select(User).where(User.email == normalize_email(email)))
    if not user or not user.is_active or not user.check_password(password):
        record_audit("auth.login_failed", event_data={"reason": "invalid_credentials"})
        db.session.commit()
        raise AuthenticationError("Invalid email or password.")
    user.last_login_at = datetime.now(UTC)
    record_audit("auth.login", actor_user_id=user.id, resource_type="user", resource_id=user.id)
    db.session.commit()
    return user


def issue_token_pair(user: User, family_id: str | None = None) -> tuple[str, str]:
    family = family_id or str(uuid.uuid4())
    claims = {"role": user.role, "family_id": family}
    access = create_access_token(identity=user.id, additional_claims=claims)
    refresh = create_refresh_token(identity=user.id, additional_claims=claims)
    decoded = decode_token(refresh)
    ip_address, user_agent = _request_metadata()
    db.session.add(
        RefreshToken(
            user_id=user.id,
            jti_hash=_hash_jti(decoded["jti"]),
            family_id=family,
            expires_at=datetime.fromtimestamp(decoded["exp"], UTC),
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    db.session.commit()
    return access, refresh


def rotate_refresh_token(user: User, claims: dict[str, Any]) -> tuple[str, str]:
    now = datetime.now(UTC)
    token_hash = _hash_jti(claims["jti"])
    result = db.session.execute(
        db.update(RefreshToken)
        .where(
            RefreshToken.jti_hash == token_hash,
            RefreshToken.used_at.is_(None),
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        .values(used_at=now)
    )
    if result.rowcount != 1:
        db.session.rollback()
        revoke_token_family(claims.get("family_id"), "refresh_reuse")
        raise AuthenticationError("The session is no longer valid.")
    record_audit("auth.refresh", actor_user_id=user.id, resource_type="user", resource_id=user.id)
    db.session.commit()
    return issue_token_pair(user, claims["family_id"])


def revoke_token(claims: dict[str, Any], reason: str) -> None:
    jti_hash = _hash_jti(claims["jti"])
    existing = db.session.scalar(
        db.select(TokenRevocation).where(TokenRevocation.jti_hash == jti_hash)
    )
    if not existing:
        db.session.add(
            TokenRevocation(
                user_id=claims["sub"],
                jti_hash=jti_hash,
                token_type=claims["type"],
                expires_at=datetime.fromtimestamp(claims["exp"], UTC),
                reason=reason,
            )
        )


def revoke_token_family(family_id: str | None, reason: str) -> None:
    if not family_id:
        return
    now = datetime.now(UTC)
    tokens = db.session.scalars(
        db.select(RefreshToken).where(
            RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None)
        )
    ).all()
    for token in tokens:
        token.revoked_at = now
    if tokens:
        record_audit(reason, actor_user_id=tokens[0].user_id)
        db.session.commit()


def revoke_all_sessions(user_id: str, reason: str = "auth.logout_all") -> None:
    now = datetime.now(UTC)
    tokens = db.session.scalars(
        db.select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        )
    ).all()
    for token in tokens:
        token.revoked_at = now
    record_audit(reason, actor_user_id=user_id, resource_type="user", resource_id=user_id)
    db.session.commit()


def is_token_revoked(claims: dict[str, Any]) -> bool:
    jti_hash = _hash_jti(claims["jti"])
    if db.session.scalar(db.select(TokenRevocation.id).where(TokenRevocation.jti_hash == jti_hash)):
        return True
    user = db.session.get(User, claims["sub"])
    if not user or not user.is_active:
        return True
    if claims.get("role") == "admin" and user.role != "admin":
        return True
    if claims["type"] == "refresh":
        token = db.session.scalar(
            db.select(RefreshToken).where(RefreshToken.jti_hash == jti_hash)
        )
        return not token or token.used_at is not None or token.revoked_at is not None
    family_id = claims.get("family_id")
    if not family_id:
        return True
    active_refresh = db.session.scalar(
        db.select(RefreshToken.id).where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.used_at.is_(None),
        )
    )
    return active_refresh is None
