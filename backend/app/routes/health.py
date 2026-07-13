from flask import Blueprint

from app.services.health_service import build_health_status
from app.utils.responses import success_response

health_blueprint = Blueprint("health", __name__)


@health_blueprint.get("/health")
def health():
    return success_response(build_health_status())

