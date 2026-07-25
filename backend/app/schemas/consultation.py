from marshmallow import Schema, ValidationError, fields, validates_schema


class ConsultationAnswerSchema(Schema):
    answer = fields.Raw(load_default=None, allow_none=True)
    skip = fields.Boolean(load_default=False)
    revision = fields.Integer(required=True, strict=True, validate=lambda value: value >= 0)

    @validates_schema
    def validate_action(self, data: dict, **kwargs) -> None:
        if data.get("skip"):
            if data.get("answer") is not None:
                raise ValidationError(
                    "A skipped question cannot also contain an answer.", "answer"
                )
        elif data.get("answer") is None:
            raise ValidationError("An answer is required unless skip is true.", "answer")


class ConsultationRevisionSchema(Schema):
    revision = fields.Integer(required=True, strict=True, validate=lambda value: value >= 0)
