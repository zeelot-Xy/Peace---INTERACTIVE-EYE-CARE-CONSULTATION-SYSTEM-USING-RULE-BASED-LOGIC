from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import User
from app.services.admin_service import (
    get_consultation_report,
    get_summary,
    list_audit_logs,
    list_consultations,
)
from app.services.knowledge_admin_service import (
    activate_version,
    get_version,
    list_versions,
    validate_upload,
)
from app.utils.auth import role_required
from app.utils.responses import error_response, success_response

admin_blueprint = Blueprint("admin", __name__)


def _pagination_args() -> tuple[int, int]:
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
    return page, per_page


@admin_blueprint.get("/users")
@jwt_required()
@role_required("admin")
def list_users():
    page, per_page = _pagination_args()
    result = db.paginate(
        db.select(User).order_by(User.created_at.desc()), page=page, per_page=per_page
    )
    return success_response(
        {
            "items": [user.to_dict() for user in result.items],
            "pagination": {
                "page": result.page,
                "per_page": result.per_page,
                "pages": result.pages,
                "total": result.total,
            },
        }
    )


@admin_blueprint.get("/summary")
@jwt_required()
@role_required("admin")
def summary():
    return success_response({"summary": get_summary()})


@admin_blueprint.get("/consultations")
@jwt_required()
@role_required("admin")
def consultations():
    page, per_page = _pagination_args()
    return success_response(list_consultations(page=page, per_page=per_page))


@admin_blueprint.get("/consultations/<consultation_id>/report")
@jwt_required()
@role_required("admin")
def consultation_report(consultation_id: str):
    report = get_consultation_report(consultation_id)
    if report is None:
        return error_response("Consultation was not found.", 404, "not_found")
    return success_response({"report": report})


@admin_blueprint.get("/audit-logs")
@jwt_required()
@role_required("admin")
def audit_logs():
    page, per_page = _pagination_args()
    return success_response(list_audit_logs(page=page, per_page=per_page))


@admin_blueprint.get("/knowledge")
@jwt_required()
@role_required("admin")
def knowledge_versions():
    return success_response({"items": list_versions()})


@admin_blueprint.get("/knowledge/<version_id>")
@jwt_required()
@role_required("admin")
def knowledge_version(version_id: str):
    return success_response({"version": get_version(version_id)})


@admin_blueprint.post("/knowledge/validate")
@jwt_required()
@role_required("admin")
def validate_knowledge():
    version = validate_upload(
        request.files.get("package"),
        get_jwt_identity(),
    )
    return success_response({"version": version}, 201)


@admin_blueprint.post("/knowledge/<version_id>/publish")
@jwt_required()
@role_required("admin")
def publish_knowledge(version_id: str):
    version = activate_version(version_id, get_jwt_identity())
    return success_response({"version": version})


@admin_blueprint.post("/knowledge/<version_id>/rollback")
@jwt_required()
@role_required("admin")
def rollback_knowledge(version_id: str):
    version = activate_version(version_id, get_jwt_identity(), rollback=True)
    return success_response({"version": version})
