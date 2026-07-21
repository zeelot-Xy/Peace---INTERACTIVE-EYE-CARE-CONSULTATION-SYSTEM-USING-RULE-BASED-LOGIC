from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import User
from app.utils.auth import role_required
from app.utils.responses import success_response

admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.get("/users")
@jwt_required()
@role_required("admin")
def list_users():
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
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
