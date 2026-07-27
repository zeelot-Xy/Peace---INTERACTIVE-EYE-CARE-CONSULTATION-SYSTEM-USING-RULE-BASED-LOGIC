import json
import os
import socket
import sqlite3
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask

from app import create_app
from app.launcher import (
    SingleInstance,
    build_parser,
    find_available_port,
    main,
    open_browser_when_ready,
    run_application,
)
from app.maintenance import (
    backup_database,
    reset_demo_database,
    restore_database,
    runtime_diagnostics,
)
from app.runtime import (
    configure_packaged_environment,
    load_or_create_installation_secrets,
    local_runtime_paths,
    seed_knowledge_packages,
)
from app.server import main as server_main
from app.server import prepare_server_environment
from app.startup import apply_database_migrations, configure_file_logging


def test_runtime_paths_are_scoped_to_selected_root(tmp_path):
    paths = local_runtime_paths(tmp_path / "client-data")

    assert paths.root == (tmp_path / "client-data").resolve()
    assert paths.database.parent == paths.root / "data"
    assert paths.knowledge_packages == paths.root / "knowledge" / "packages"
    assert paths.secrets_file.parent == paths.root / "config"


def test_runtime_paths_use_local_app_data(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    paths = local_runtime_paths()

    assert paths.root == (tmp_path / "EyeCareConsultation").resolve()


def test_installation_secrets_are_persistent_and_private(tmp_path):
    secret_file = tmp_path / "config" / "installation-secrets.json"

    first = load_or_create_installation_secrets(secret_file)
    second = load_or_create_installation_secrets(secret_file)

    assert first == second
    assert first["secret_key"] != first["jwt_secret_key"]
    assert len(first["secret_key"]) >= 32
    assert "secret_key" in json.loads(secret_file.read_text(encoding="utf-8"))
    if os.name != "nt":
        assert secret_file.stat().st_mode & 0o077 == 0


def test_invalid_installation_secret_file_fails_closed(tmp_path):
    secret_file = tmp_path / "installation-secrets.json"
    secret_file.write_text('{"secret_key": "short"}', encoding="utf-8")

    with pytest.raises(RuntimeError, match="invalid"):
        load_or_create_installation_secrets(secret_file)


def test_seed_knowledge_copies_only_missing_packages(tmp_path):
    source = tmp_path / "bundled"
    package = source / "eye-care-en-1.0.0"
    package.mkdir(parents=True)
    (package / "manifest.json").write_text('{"version": 1}', encoding="utf-8")
    destination = tmp_path / "runtime"

    seed_knowledge_packages(destination, source)
    runtime_manifest = destination / package.name / "manifest.json"
    runtime_manifest.write_text('{"preserved": true}', encoding="utf-8")
    seed_knowledge_packages(destination, source)

    assert runtime_manifest.read_text(encoding="utf-8") == '{"preserved": true}'


def test_packaged_environment_initializes_writable_state(tmp_path, monkeypatch):
    paths = local_runtime_paths(tmp_path / "runtime")
    for name in (
        "APP_ENV",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "KNOWLEDGE_PACKAGES_DIR",
        "KNOWLEDGE_SCHEMAS_DIR",
        "KNOWLEDGE_STATE_FILE",
        "STATIC_DIST_DIR",
        "CORS_ORIGINS",
    ):
        monkeypatch.setenv(name, f"original-{name.lower()}")
    monkeypatch.setattr(
        "app.runtime.resource_path",
        lambda relative: (
            Path(__file__).parents[1] / relative
            if str(relative).startswith("knowledge/")
            else tmp_path / relative
        ),
    )

    overrides = configure_packaged_environment(
        paths,
        static_directory=tmp_path / "static",
    )

    assert os.environ["APP_ENV"] == "packaged"
    assert os.environ["DATABASE_URL"].startswith("sqlite:///")
    assert Path(os.environ["KNOWLEDGE_PACKAGES_DIR"]).is_dir()
    assert paths.secrets_file.is_file()
    assert overrides["SQLALCHEMY_DATABASE_URI"].endswith("/data/eye-care.sqlite3")


def test_static_frontend_and_spa_fallback_are_served(tmp_path):
    static = tmp_path / "static"
    assets = static / "assets"
    assets.mkdir(parents=True)
    (static / "index.html").write_text("<html>release</html>", encoding="utf-8")
    (assets / "app.js").write_text("console.log('release')", encoding="utf-8")
    application = create_app(
        "testing",
        {
            "STATIC_DIST_DIR": str(static),
        },
    )
    client = application.test_client()

    assert client.get("/").data == b"<html>release</html>"
    assert client.get("/consultations/example").data == b"<html>release</html>"
    assert client.get("/assets/app.js").mimetype == "text/javascript"
    assert "default-src 'self'" in client.get("/").headers["Content-Security-Policy"]
    missing_api = client.get("/api/v1/not-a-route")
    assert missing_api.status_code == 404
    assert missing_api.get_json()["errors"][0]["code"] == "not_found"


def test_available_port_skips_an_occupied_preferred_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
        occupied.bind(("127.0.0.1", 0))
        preferred = int(occupied.getsockname()[1])

        selected = find_available_port(preferred)

    assert selected != preferred


def test_ready_browser_opener_uses_health_endpoint(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    response = Response()
    urlopen = Mock(return_value=response)
    browser = Mock()
    monkeypatch.setattr("app.launcher.urllib.request.urlopen", urlopen)
    monkeypatch.setattr("app.launcher.webbrowser.open", browser)

    open_browser_when_ready("http://127.0.0.1:8765")

    assert urlopen.call_args.args[0].endswith("/api/v1/health")
    browser.assert_called_once_with("http://127.0.0.1:8765")


def test_single_instance_rejects_second_lock(tmp_path):
    lock_file = tmp_path / "runtime.lock"

    with SingleInstance(lock_file):
        with pytest.raises(RuntimeError, match="already running"):
            with SingleInstance(lock_file):
                pass


def test_database_backup_restore_and_diagnostics(tmp_path):
    paths = local_runtime_paths(tmp_path / "runtime")
    paths.database.parent.mkdir(parents=True)
    with closing(sqlite3.connect(paths.database)) as connection:
        connection.execute("CREATE TABLE sample (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sample VALUES ('original')")
        connection.commit()

    backup = backup_database(paths)
    with closing(sqlite3.connect(paths.database)) as connection:
        connection.execute("UPDATE sample SET value = 'changed'")
        connection.commit()

    restore_database(paths, backup)

    with closing(sqlite3.connect(paths.database)) as connection:
        assert connection.execute("SELECT value FROM sample").fetchone()[0] == "original"
    diagnostics = json.loads(runtime_diagnostics(paths))
    assert diagnostics["database_integrity"] == "ok"
    assert diagnostics["backup_count"] == 1


def test_restore_rejects_invalid_database(tmp_path):
    paths = local_runtime_paths(tmp_path / "runtime")
    invalid = tmp_path / "not-a-database.sqlite3"
    invalid.write_text("invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="valid SQLite"):
        restore_database(paths, invalid)


def test_demo_reset_creates_safety_backup(tmp_path):
    paths = local_runtime_paths(tmp_path / "runtime")
    paths.database.parent.mkdir(parents=True)
    with closing(sqlite3.connect(paths.database)) as connection:
        connection.execute("CREATE TABLE sample (value TEXT NOT NULL)")
        connection.commit()

    backup = reset_demo_database(paths)

    assert backup is not None and backup.is_file()
    assert not paths.database.exists()


def test_launcher_parser_defaults_to_run():
    parser = build_parser()

    assert parser.parse_args([]).command is None
    assert parser.parse_args(["run", "--no-browser"]).no_browser is True


def test_launcher_run_coordinates_startup(monkeypatch, tmp_path):
    logger = Mock()
    application = SimpleNamespace(logger=logger)
    calls: list[str] = []
    monkeypatch.setattr(
        "app.launcher.configure_packaged_environment",
        lambda paths: calls.append("environment"),
    )
    monkeypatch.setattr(
        "app.launcher.create_app",
        lambda profile, overrides: application,
    )
    monkeypatch.setattr(
        "app.launcher.configure_file_logging",
        lambda app, logs: calls.append("logging"),
    )
    monkeypatch.setattr(
        "app.launcher.apply_database_migrations",
        lambda app: calls.append("migrations"),
    )
    monkeypatch.setattr("app.launcher.find_available_port", lambda preferred: 8877)
    monkeypatch.setattr(
        "app.launcher.serve",
        lambda app, **kwargs: calls.append(f"serve:{kwargs['port']}"),
    )
    args = SimpleNamespace(
        data_directory=str(tmp_path / "runtime"),
        port=8765,
        no_browser=True,
    )

    assert run_application(args) == 0
    assert calls == ["environment", "logging", "migrations", "serve:8877"]


def test_launcher_maintenance_commands(monkeypatch, tmp_path, capsys):
    data_directory = str(tmp_path / "runtime")
    backup = tmp_path / "backup.sqlite3"
    monkeypatch.setattr("app.launcher.backup_database", lambda paths, output: backup)
    monkeypatch.setattr("app.launcher.restore_database", lambda paths, source: None)
    monkeypatch.setattr("app.launcher.reset_demo_database", lambda paths: backup)
    monkeypatch.setattr("app.launcher.runtime_diagnostics", lambda paths: '{"status":"ok"}')

    assert main(["--data-directory", data_directory, "backup"]) == 0
    assert main(
        [
            "--data-directory",
            data_directory,
            "restore",
            str(backup),
            "--confirm",
        ]
    ) == 0
    assert main(
        ["--data-directory", data_directory, "reset-demo-data", "--confirm"]
    ) == 0
    assert main(["--data-directory", data_directory, "diagnostics"]) == 0
    output = capsys.readouterr().out
    assert "Backup created" in output
    assert "restored successfully" in output
    assert "Demo data reset" in output
    assert '"status":"ok"' in output


def test_launcher_reports_runtime_failure(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        "app.launcher.runtime_diagnostics",
        Mock(side_effect=RuntimeError("broken runtime")),
    )

    result = main(
        ["--data-directory", str(tmp_path / "runtime"), "diagnostics"]
    )

    assert result == 1
    assert "broken runtime" in capsys.readouterr().err


def test_startup_logging_and_migration_helpers(monkeypatch, tmp_path):
    application = Flask("startup-test")
    upgrade = Mock()
    monkeypatch.setattr("app.startup.upgrade", upgrade)
    migrations = tmp_path / "migrations"
    migrations.mkdir()

    log_file = configure_file_logging(application, tmp_path / "logs")
    apply_database_migrations(application, migrations)

    application.logger.info("packaged startup")
    for handler in application.logger.handlers:
        handler.flush()
    assert log_file.is_file()
    upgrade.assert_called_once_with(directory=str(migrations))


def test_missing_migrations_fail_closed(tmp_path):
    with pytest.raises(RuntimeError, match="migrations are missing"):
        apply_database_migrations(Flask("missing-migrations"), tmp_path / "missing")


def test_server_environment_uses_persistent_data(monkeypatch, tmp_path):
    packages = tmp_path / "data" / "knowledge" / "packages"
    seeded: list[Path] = []
    for name in (
        "APP_ENV",
        "DATABASE_URL",
        "KNOWLEDGE_PACKAGES_DIR",
        "KNOWLEDGE_SCHEMAS_DIR",
        "KNOWLEDGE_STATE_FILE",
        "STATIC_DIST_DIR",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(
        "app.server.seed_knowledge_packages",
        lambda destination: seeded.append(destination),
    )
    monkeypatch.setattr(
        "app.server.resource_path",
        lambda relative: tmp_path / relative,
    )

    overrides = prepare_server_environment()

    assert seeded == [packages.resolve()]
    assert os.environ["APP_ENV"] == "production"
    assert os.environ["DATABASE_URL"].endswith("/data/eye-care.sqlite3")
    assert os.environ["STATIC_DIST_DIR"].endswith("static")
    assert overrides["SQLALCHEMY_DATABASE_URI"].endswith("/data/eye-care.sqlite3")


def test_server_main_migrates_before_serving(monkeypatch):
    calls: list[str] = []
    application = object()
    monkeypatch.setattr(
        "app.server.prepare_server_environment",
        lambda: calls.append("environment"),
    )
    monkeypatch.setattr(
        "app.server.create_app",
        lambda profile, overrides: application,
    )
    monkeypatch.setattr(
        "app.server.apply_database_migrations",
        lambda app: calls.append("migrations"),
    )
    monkeypatch.setattr(
        "app.server.serve",
        lambda app, **kwargs: calls.append(f"serve:{kwargs['port']}"),
    )
    monkeypatch.setenv("PORT", "5055")

    server_main()

    assert calls == ["environment", "migrations", "serve:5055"]
