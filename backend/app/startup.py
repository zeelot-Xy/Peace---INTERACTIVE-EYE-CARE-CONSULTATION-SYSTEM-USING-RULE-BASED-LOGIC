import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from flask_migrate import upgrade

from app.runtime import resource_path


def configure_file_logging(app: Flask, logs_directory: Path) -> Path:
    logs_directory.mkdir(parents=True, exist_ok=True)
    log_path = logs_directory / "eye-care.log"
    handler = RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    return log_path


def apply_database_migrations(app: Flask, migrations_directory: Path | None = None) -> None:
    directory = migrations_directory or resource_path("migrations")
    if not directory.is_dir():
        raise RuntimeError(f"Database migrations are missing: {directory}")
    with app.app_context():
        upgrade(directory=str(directory))
