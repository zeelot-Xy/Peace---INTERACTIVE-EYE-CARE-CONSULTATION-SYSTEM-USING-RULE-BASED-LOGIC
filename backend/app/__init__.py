import json
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.commands import register_commands
from app.config import get_config
from app.extensions import db, jwt, migrate
from app.inference import InferenceEngine
from app.knowledge import KnowledgeLoadError, KnowledgeManager
from app.routes.admin import admin_blueprint
from app.routes.auth import auth_blueprint
from app.routes.consultations import consultations_blueprint
from app.routes.health import health_blueprint
from app.routes.users import users_blueprint
from app.services.auth_service import is_token_revoked
from app.utils.responses import error_response, register_error_handlers


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, connection_record) -> None:
    if connection.__class__.__module__.startswith("sqlite3"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(
    config_name: str | None = None, config_overrides: dict[str, object] | None = None
) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)
    if config_overrides:
        app.config.update(config_overrides)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    packages_dir = Path(app.config["KNOWLEDGE_PACKAGES_DIR"]).resolve()
    state_file = Path(
        app.config["KNOWLEDGE_STATE_FILE"]
        or Path(app.instance_path) / "knowledge-active.json"
    ).resolve()
    app.config["KNOWLEDGE_PACKAGES_DIR"] = str(packages_dir)
    app.config["KNOWLEDGE_STATE_FILE"] = str(state_file)
    active_package = app.config["KNOWLEDGE_ACTIVE_PACKAGE"]
    expected_fingerprint = None
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            candidate = state["package_id"]
            if not isinstance(candidate, str) or Path(candidate).name != candidate:
                raise ValueError("Invalid active package identifier.")
            active_package = candidate
            expected_fingerprint = state.get("fingerprint")
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            raise KnowledgeLoadError("The active knowledge state file is invalid.") from error

    knowledge = KnowledgeManager(Path(app.config["KNOWLEDGE_SCHEMAS_DIR"]))
    active_path = packages_dir / active_package
    report = knowledge.activate(active_path)
    if not report.valid:
        codes = ", ".join(sorted({issue.code for issue in report.issues}))
        raise KnowledgeLoadError(
            f"Unable to start without a valid knowledge package "
            f"'{app.config['KNOWLEDGE_ACTIVE_PACKAGE']}': {codes}."
        )
    if expected_fingerprint and report.fingerprint != expected_fingerprint:
        raise KnowledgeLoadError(
            "The active knowledge package does not match its published fingerprint."
        )
    app.extensions["knowledge"] = knowledge
    app.extensions["inference"] = InferenceEngine()
    app.logger.info("Activated knowledge package %s (%s).", report.package_id, report.fingerprint)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )
    app.register_blueprint(health_blueprint, url_prefix="/api/v1")
    app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")
    app.register_blueprint(users_blueprint, url_prefix="/api/v1/users")
    app.register_blueprint(admin_blueprint, url_prefix="/api/v1/admin")
    app.register_blueprint(
        consultations_blueprint, url_prefix="/api/v1/consultations"
    )
    register_commands(app)
    register_error_handlers(app)

    @jwt.token_in_blocklist_loader
    def token_in_blocklist(jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return error_response("Authentication is required.", 401, "authentication_required")

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return error_response("The session token is invalid.", 401, "invalid_token")

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return error_response("The session has expired.", 401, "token_expired")

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        if jwt_payload.get("type") == "refresh":
            from app.services.auth_service import revoke_token_family

            revoke_token_family(jwt_payload.get("family_id"), "auth.refresh_reuse")
        return error_response("The session is no longer valid.", 401, "token_revoked")

    return app
