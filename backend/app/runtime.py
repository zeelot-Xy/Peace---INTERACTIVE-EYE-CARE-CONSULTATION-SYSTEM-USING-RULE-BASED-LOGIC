import json
import os
import secrets
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from app.config import BACKEND_ROOT

APPLICATION_DIRECTORY_NAME = "EyeCareConsultation"
SECRET_FILE_NAME = "installation-secrets.json"


def resource_path(relative_path: str | Path) -> Path:
    """Resolve a bundled resource in source and PyInstaller runtimes."""
    bundle_root = Path(getattr(sys, "_MEIPASS", BACKEND_ROOT))
    return (bundle_root / relative_path).resolve()


@dataclass(frozen=True)
class RuntimePaths:
    root: Path
    database: Path
    logs: Path
    backups: Path
    knowledge_packages: Path
    knowledge_state: Path
    secrets_file: Path


def local_runtime_paths(root: Path | None = None) -> RuntimePaths:
    if root is None:
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            root = Path(local_app_data) / APPLICATION_DIRECTORY_NAME
        else:
            root = Path.home() / ".local" / "share" / APPLICATION_DIRECTORY_NAME
    resolved_root = root.expanduser().resolve()
    return RuntimePaths(
        root=resolved_root,
        database=resolved_root / "data" / "eye-care.sqlite3",
        logs=resolved_root / "logs",
        backups=resolved_root / "backups",
        knowledge_packages=resolved_root / "knowledge" / "packages",
        knowledge_state=resolved_root / "knowledge" / "active.json",
        secrets_file=resolved_root / "config" / SECRET_FILE_NAME,
    )


def ensure_runtime_directories(paths: RuntimePaths) -> None:
    for directory in (
        paths.database.parent,
        paths.logs,
        paths.backups,
        paths.knowledge_packages,
        paths.knowledge_state.parent,
        paths.secrets_file.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def seed_knowledge_packages(
    destination: Path,
    source: Path | None = None,
) -> None:
    """Copy only absent bundled packages into the writable runtime directory."""
    source_directory = source or resource_path("knowledge/packages")
    if not source_directory.is_dir():
        raise RuntimeError(f"Bundled knowledge packages are missing: {source_directory}")
    destination.mkdir(parents=True, exist_ok=True)
    for package in source_directory.iterdir():
        target = destination / package.name
        if package.is_dir() and not target.exists():
            shutil.copytree(package, target)


def load_or_create_installation_secrets(path: Path) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError("The installation secret file cannot be read.") from error
        if not isinstance(payload, dict) or any(
            not isinstance(payload.get(key), str) or len(payload[key]) < 32
            for key in ("secret_key", "jwt_secret_key")
        ):
            raise RuntimeError("The installation secret file is invalid.")
        return {
            "secret_key": payload["secret_key"],
            "jwt_secret_key": payload["jwt_secret_key"],
        }

    payload = {
        "secret_key": secrets.token_urlsafe(48),
        "jwt_secret_key": secrets.token_urlsafe(48),
    }
    encoded = json.dumps(payload, indent=2).encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        os.write(descriptor, encoded)
    finally:
        os.close(descriptor)
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return payload


def sqlite_uri(path: Path) -> str:
    return f"sqlite:///{path.resolve().as_posix()}"


def configure_packaged_environment(
    paths: RuntimePaths,
    *,
    static_directory: Path | None = None,
) -> dict[str, object]:
    """Set the packaged profile before Flask configuration is constructed."""
    ensure_runtime_directories(paths)
    seed_knowledge_packages(paths.knowledge_packages)
    installation_secrets = load_or_create_installation_secrets(paths.secrets_file)
    environment = {
        "APP_ENV": "packaged",
        "SECRET_KEY": installation_secrets["secret_key"],
        "JWT_SECRET_KEY": installation_secrets["jwt_secret_key"],
        "DATABASE_URL": sqlite_uri(paths.database),
        "KNOWLEDGE_PACKAGES_DIR": str(paths.knowledge_packages),
        "KNOWLEDGE_SCHEMAS_DIR": str(resource_path("knowledge/schemas")),
        "KNOWLEDGE_STATE_FILE": str(paths.knowledge_state),
        "STATIC_DIST_DIR": str(static_directory or resource_path("static")),
        "CORS_ORIGINS": "http://127.0.0.1",
    }
    os.environ.update(environment)
    return {
        "SECRET_KEY": installation_secrets["secret_key"],
        "JWT_SECRET_KEY": installation_secrets["jwt_secret_key"],
        "DATABASE_URL": sqlite_uri(paths.database),
        "SQLALCHEMY_DATABASE_URI": sqlite_uri(paths.database),
        "KNOWLEDGE_PACKAGES_DIR": str(paths.knowledge_packages),
        "KNOWLEDGE_SCHEMAS_DIR": str(resource_path("knowledge/schemas")),
        "KNOWLEDGE_STATE_FILE": str(paths.knowledge_state),
        "STATIC_DIST_DIR": str(static_directory or resource_path("static")),
        "CORS_ORIGINS": ("http://127.0.0.1",),
        "JWT_COOKIE_SECURE": False,
    }
