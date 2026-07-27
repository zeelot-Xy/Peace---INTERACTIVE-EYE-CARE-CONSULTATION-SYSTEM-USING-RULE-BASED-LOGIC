from flask import request
from marshmallow import Schema, ValidationError


class RequestValidationError(Exception):
    def __init__(self, errors: dict):
        super().__init__("Request validation failed.")
        self.errors = errors


def load_json(schema: Schema) -> dict:
    if not request.is_json:
        raise RequestValidationError(
            {"body": ["Content-Type must be application/json."]}
        )
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise RequestValidationError({"body": ["A JSON object is required."]})
    try:
        return schema.load(payload)
    except ValidationError as error:
        raise RequestValidationError(error.messages) from error
