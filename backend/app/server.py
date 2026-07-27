import os
from pathlib import Path

from waitress import serve

from app import create_app
from app.runtime import resource_path, seed_knowledge_packages
from app.startup import apply_database_migrations


def prepare_server_environment() -> dict[str, object]:
    data_root = Path(os.getenv("APP_DATA_DIR", "/data")).resolve()
    packages = Path(
        os.getenv("KNOWLEDGE_PACKAGES_DIR", data_root / "knowledge" / "packages")
    ).resolve()
    packages.mkdir(parents=True, exist_ok=True)
    seed_knowledge_packages(packages)
    os.environ.setdefault("APP_ENV", "production")
    database_uri = f"sqlite:///{(data_root / 'eye-care.sqlite3').as_posix()}"
    os.environ.setdefault("DATABASE_URL", database_uri)
    os.environ.setdefault("KNOWLEDGE_PACKAGES_DIR", str(packages))
    os.environ.setdefault("KNOWLEDGE_SCHEMAS_DIR", str(resource_path("knowledge/schemas")))
    os.environ.setdefault(
        "KNOWLEDGE_STATE_FILE",
        str(data_root / "knowledge" / "active.json"),
    )
    os.environ.setdefault("STATIC_DIST_DIR", str(resource_path("static")))
    return {
        "DATABASE_URL": database_uri,
        "SQLALCHEMY_DATABASE_URI": database_uri,
        "KNOWLEDGE_PACKAGES_DIR": str(packages),
        "KNOWLEDGE_SCHEMAS_DIR": str(resource_path("knowledge/schemas")),
        "KNOWLEDGE_STATE_FILE": str(data_root / "knowledge" / "active.json"),
        "STATIC_DIST_DIR": str(resource_path("static")),
    }


def main() -> None:
    config_overrides = prepare_server_environment()
    app = create_app("production", config_overrides)
    apply_database_migrations(app)
    port = int(os.getenv("PORT", "5000"))
    serve(app, host="0.0.0.0", port=port, threads=4)


if __name__ == "__main__":
    main()
