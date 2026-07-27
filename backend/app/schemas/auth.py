from marshmallow import Schema, ValidationError, fields, validates, validates_schema

from app.utils.security import normalize_text


class NormalizedString(fields.String):
    def __init__(self, *args, field_label: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_label = field_label

    def _deserialize(self, value, attr, data, **kwargs):
        result = super()._deserialize(value, attr, data, **kwargs)
        try:
            return normalize_text(
                result,
                max_length=self.metadata.get("max_length", 120),
                field_name=self.field_label,
            )
        except ValueError as error:
            raise ValidationError(str(error)) from error


class RegistrationSchema(Schema):
    full_name = NormalizedString(
        required=True,
        field_label="Full name",
        metadata={"max_length": 120},
    )
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

    @validates("full_name")
    def validate_name(self, value: str, **kwargs) -> None:
        if not 2 <= len(value.strip()) <= 120:
            raise ValidationError("Full name must be between 2 and 120 characters.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class ProfileUpdateSchema(Schema):
    full_name = NormalizedString(
        load_default=None,
        allow_none=True,
        field_label="Full name",
        metadata={"max_length": 120},
    )
    phone = NormalizedString(
        load_default=None,
        allow_none=True,
        field_label="Phone",
        metadata={"max_length": 30},
    )
    date_of_birth = fields.Date(load_default=None, allow_none=True)

    @validates_schema
    def validate_profile(self, data: dict, **kwargs) -> None:
        if not data:
            raise ValidationError("At least one profile field is required.", field_name="profile")
        if data.get("full_name") is not None and not 2 <= len(data["full_name"].strip()) <= 120:
            raise ValidationError("Full name must be between 2 and 120 characters.", "full_name")
        if data.get("phone") is not None and len(data["phone"].strip()) > 30:
            raise ValidationError("Phone number must not exceed 30 characters.", "phone")


class PasswordChangeSchema(Schema):
    current_password = fields.String(required=True, load_only=True)
    new_password = fields.String(required=True, load_only=True)
