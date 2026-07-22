import os
import secrets
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _as_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _application_secret() -> str:
    return os.getenv("SECRET_KEY") or secrets.token_urlsafe(48)


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or secrets.token_urlsafe(48)


@dataclass(frozen=True)
class BaseConfig:
    SECRET_KEY: str = field(default_factory=_application_secret)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///eye_care.db")
    CORS_ORIGINS: tuple[str, ...] = tuple(_cors_origins())
    JSON_SORT_KEYS: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///eye_care.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    JWT_SECRET_KEY: str = field(default_factory=_jwt_secret)
    JWT_TOKEN_LOCATION: tuple[str, ...] = ("cookies",)
    JWT_COOKIE_CSRF_PROTECT: bool = True
    JWT_COOKIE_SECURE: bool = _as_bool("JWT_COOKIE_SECURE")
    JWT_COOKIE_SAMESITE: str = "Lax"
    JWT_ACCESS_COOKIE_PATH: str = "/api/v1"
    JWT_REFRESH_COOKIE_PATH: str = "/api/v1/auth"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(
        days=int(os.getenv("REFRESH_TOKEN_DAYS", "7"))
    )
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "12"))
    PASSWORD_MAX_LENGTH: int = 128
    KNOWLEDGE_PACKAGES_DIR: str = os.getenv(
        "KNOWLEDGE_PACKAGES_DIR", str(BACKEND_ROOT / "knowledge" / "packages")
    )
    KNOWLEDGE_SCHEMAS_DIR: str = os.getenv(
        "KNOWLEDGE_SCHEMAS_DIR", str(BACKEND_ROOT / "knowledge" / "schemas")
    )
    KNOWLEDGE_ACTIVE_PACKAGE: str = os.getenv(
        "KNOWLEDGE_ACTIVE_PACKAGE", "eye-care-en-1.0.0"
    )
    KNOWLEDGE_RELOAD_ON_CHANGE: bool = _as_bool("KNOWLEDGE_RELOAD_ON_CHANGE")


@dataclass(frozen=True)
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


@dataclass(frozen=True)
class TestingConfig(BaseConfig):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"
    JWT_COOKIE_SECURE: bool = False


@dataclass(frozen=True)
class ProductionConfig(BaseConfig):
    DEBUG: bool = False


CONFIGURATIONS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "packaged": ProductionConfig,
}


def get_config(config_name: str | None = None) -> BaseConfig:
    selected = config_name or os.getenv("APP_ENV", "development")
    normalized = selected.lower()
    config_type = CONFIGURATIONS.get(normalized)
    if config_type is None:
        allowed = ", ".join(sorted(CONFIGURATIONS))
        raise ValueError(f"Unknown APP_ENV '{selected}'. Expected one of: {allowed}")
    if normalized in {"production", "packaged"}:
        application_secret = os.getenv("SECRET_KEY", "")
        jwt_secret = os.getenv("JWT_SECRET_KEY") or application_secret
        if len(application_secret) < 32 or len(jwt_secret) < 32:
            raise RuntimeError(
                "SECRET_KEY and JWT_SECRET_KEY must contain at least 32 characters "
                "outside development."
            )
    return config_type()
