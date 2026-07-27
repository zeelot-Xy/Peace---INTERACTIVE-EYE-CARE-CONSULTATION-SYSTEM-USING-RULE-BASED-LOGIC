import os
import secrets
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    origins = [origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip()]
    if not origins:
        raise RuntimeError("CORS_ORIGINS must contain at least one explicit origin.")
    for origin in origins:
        parsed = urlsplit(origin)
        if (
            origin == "*"
            or parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise RuntimeError(
                "CORS_ORIGINS must contain only explicit HTTP(S) origins without "
                "credentials, paths, queries, fragments, or wildcards."
            )
    return origins


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
    CORS_ORIGINS: tuple[str, ...] = field(
        default_factory=lambda: tuple(_cors_origins())
    )
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
    MAX_CONTENT_LENGTH: int = int(
        os.getenv("REQUEST_MAX_BYTES", str(6 * 1024 * 1024))
    )
    RATELIMIT_ENABLED: bool = _as_bool("RATELIMIT_ENABLED", True)
    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "300 per minute")
    RATELIMIT_LOGIN: str = os.getenv("RATELIMIT_LOGIN", "5 per minute")
    RATELIMIT_REGISTER: str = os.getenv("RATELIMIT_REGISTER", "5 per 5 minutes")
    RATELIMIT_REFRESH: str = os.getenv("RATELIMIT_REFRESH", "20 per minute")
    RATELIMIT_KNOWLEDGE_UPLOAD: str = os.getenv(
        "RATELIMIT_KNOWLEDGE_UPLOAD", "10 per 10 minutes"
    )
    SECURITY_HSTS_SECONDS: int = int(
        os.getenv("SECURITY_HSTS_SECONDS", "31536000")
    )
    RETENTION_ABANDONED_DAYS: int = int(
        os.getenv("RETENTION_ABANDONED_DAYS", "90")
    )
    RETENTION_COMPLETED_DAYS: int = int(
        os.getenv("RETENTION_COMPLETED_DAYS", "365")
    )
    RETENTION_TOKEN_DAYS: int = int(os.getenv("RETENTION_TOKEN_DAYS", "30"))
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
    KNOWLEDGE_STATE_FILE: str = os.getenv("KNOWLEDGE_STATE_FILE", "")
    KNOWLEDGE_UPLOAD_MAX_BYTES: int = int(
        os.getenv("KNOWLEDGE_UPLOAD_MAX_BYTES", str(5 * 1024 * 1024))
    )
    KNOWLEDGE_ARCHIVE_MAX_ENTRIES: int = int(
        os.getenv("KNOWLEDGE_ARCHIVE_MAX_ENTRIES", "16")
    )
    KNOWLEDGE_ARCHIVE_MAX_COMPRESSION_RATIO: int = int(
        os.getenv("KNOWLEDGE_ARCHIVE_MAX_COMPRESSION_RATIO", "100")
    )


@dataclass(frozen=True)
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


@dataclass(frozen=True)
class TestingConfig(BaseConfig):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"
    JWT_COOKIE_SECURE: bool = False
    RATELIMIT_ENABLED: bool = False


@dataclass(frozen=True)
class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    JWT_COOKIE_SECURE: bool = True


@dataclass(frozen=True)
class PackagedConfig(BaseConfig):
    DEBUG: bool = False
    JWT_COOKIE_SECURE: bool = False


CONFIGURATIONS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "packaged": PackagedConfig,
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
