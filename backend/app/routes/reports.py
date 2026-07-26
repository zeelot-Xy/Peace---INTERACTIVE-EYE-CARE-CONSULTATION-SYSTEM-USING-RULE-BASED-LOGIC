from io import BytesIO

from flask import Blueprint, send_file
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services.report_service import (
    get_report,
    get_report_file,
    list_reports,
)
from app.utils.responses import error_response, success_response

reports_blueprint = Blueprint("reports", __name__)


def _pagination_args() -> tuple[int, int] | None:
    from flask import request

    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 20)), 1), 50)
    except ValueError:
        return None
    return page, per_page


@reports_blueprint.get("")
@jwt_required()
def index():
    pagination = _pagination_args()
    if pagination is None:
        return error_response(
            "Pagination values must be integers.", 422, "validation_error"
        )
    return success_response(
        list_reports(
            get_jwt_identity(),
            get_jwt().get("role", "patient"),
            page=pagination[0],
            per_page=pagination[1],
        )
    )


@reports_blueprint.get("/<report_id>")
@jwt_required()
def detail(report_id: str):
    return success_response(
        {
            "report": get_report(
                report_id,
                get_jwt_identity(),
                get_jwt().get("role", "patient"),
            )
        }
    )


@reports_blueprint.get("/<report_id>/download")
@jwt_required()
def download(report_id: str):
    pdf_data, filename, content_type = get_report_file(
        report_id,
        get_jwt_identity(),
        get_jwt().get("role", "patient"),
    )
    response = send_file(
        BytesIO(pdf_data),
        mimetype=content_type,
        as_attachment=True,
        download_name=filename,
        max_age=0,
    )
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
