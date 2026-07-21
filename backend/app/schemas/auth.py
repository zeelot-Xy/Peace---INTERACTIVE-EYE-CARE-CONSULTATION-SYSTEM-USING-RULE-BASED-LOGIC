from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class RegistrationSchema(Schema):
    full_name = fields.String(required=True)
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
    full_name = fields.String(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True)
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
