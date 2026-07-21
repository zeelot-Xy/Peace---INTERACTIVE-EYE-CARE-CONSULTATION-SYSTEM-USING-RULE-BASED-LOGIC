import pytest

from app import create_app
from app.config import get_config


def test_production_rejects_missing_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="at least 32 characters"):
        create_app("production")


def test_production_rejects_short_secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "x" * 31)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="at least 32 characters"):
        create_app("production")


def test_production_accepts_environment_secret(monkeypatch):
    environment_secret = "x" * 32
    monkeypatch.setenv("SECRET_KEY", environment_secret)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    application = create_app("production")

    assert application.config["SECRET_KEY"] == environment_secret
    assert application.config["JWT_SECRET_KEY"] == environment_secret


def test_testing_config_generates_runtime_secrets(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    config = get_config("testing")

    assert len(config.SECRET_KEY) >= 32
    assert len(config.JWT_SECRET_KEY) >= 32
