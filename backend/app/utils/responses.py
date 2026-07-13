from typing import Any
from uuid import uuid4

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


def _correlation_id() -> str:
    return request.headers.get("X-Correlation-ID", str(uuid4()))


def success_response(data: Any, status_code: int = 200):
    return jsonify({"data": data, "errors": [], "correlation_id": _correlation_id()}), status_code


def error_response(message: str, status_code: int, code: str):
    payload = {
        "data": None,
        "errors": [{"code": code, "message": message}],
        "correlation_id": _correlation_id(),
    }
    return jsonify(payload), status_code


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        error_code = error.name.lower().replace(" ", "_")
        return error_response(error.description, error.code or 500, error_code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled application error", exc_info=error)
        return error_response("An unexpected error occurred.", 500, "internal_server_error")
