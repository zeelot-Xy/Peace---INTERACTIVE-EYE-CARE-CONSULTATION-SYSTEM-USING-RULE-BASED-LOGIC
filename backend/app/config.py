import os
from dataclasses import dataclass


def _cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@dataclass(frozen=True)
class BaseConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-only-secret-change-me")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///instance/eye_care.db")
    CORS_ORIGINS: tuple[str, ...] = tuple(_cors_origins())
    JSON_SORT_KEYS: bool = False


@dataclass(frozen=True)
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


@dataclass(frozen=True)
class TestingConfig(BaseConfig):
    TESTING: bool = True
    SECRET_KEY: str = "test-secret-key"


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
    config_type = CONFIGURATIONS.get(selected.lower())
    if config_type is None:
        allowed = ", ".join(sorted(CONFIGURATIONS))
        raise ValueError(f"Unknown APP_ENV '{selected}'. Expected one of: {allowed}")
    return config_type()

