from app.schemas.auth import (
    LoginSchema,
    PasswordChangeSchema,
    ProfileUpdateSchema,
    RegistrationSchema,
)
from app.schemas.consultation import ConsultationAnswerSchema, ConsultationRevisionSchema

__all__ = [
    "ConsultationAnswerSchema",
    "ConsultationRevisionSchema",
    "LoginSchema",
    "PasswordChangeSchema",
    "ProfileUpdateSchema",
    "RegistrationSchema",
]
