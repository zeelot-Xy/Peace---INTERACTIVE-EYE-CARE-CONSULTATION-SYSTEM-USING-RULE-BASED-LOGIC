import json
import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from app.runtime import RuntimePaths, ensure_runtime_directories


def _verify_sqlite_database(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Database file does not exist: {path}")
    try:
        with closing(
            sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        ) as connection:
            result = connection.execute("PRAGMA quick_check").fetchone()
    except sqlite3.DatabaseError as error:
        raise ValueError("The selected file is not a valid SQLite database.") from error
    if not result or result[0] != "ok":
        raise ValueError("The selected database did not pass its integrity check.")


def backup_database(paths: RuntimePaths, output: Path | None = None) -> Path:
    ensure_runtime_directories(paths)
    _verify_sqlite_database(paths.database)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    destination = (output or paths.backups / f"eye-care-{timestamp}.sqlite3").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(f"{destination.suffix}.tmp")
    if temporary.exists():
        temporary.unlink()
    try:
        with (
            closing(sqlite3.connect(paths.database)) as source,
            closing(sqlite3.connect(temporary)) as target,
        ):
            source.backup(target)
            target.commit()
        _verify_sqlite_database(temporary)
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination


def restore_database(paths: RuntimePaths, backup: Path) -> None:
    ensure_runtime_directories(paths)
    source = backup.expanduser().resolve()
    _verify_sqlite_database(source)
    if source == paths.database.resolve():
        raise ValueError("The active database cannot be restored onto itself.")
    temporary = paths.database.with_suffix(".restore.tmp")
    rollback = paths.database.with_suffix(".before-restore")
    shutil.copy2(source, temporary)
    _verify_sqlite_database(temporary)
    if rollback.exists():
        rollback.unlink()
    if paths.database.exists():
        paths.database.replace(rollback)
    try:
        temporary.replace(paths.database)
        _verify_sqlite_database(paths.database)
    except Exception:
        if paths.database.exists():
            paths.database.unlink()
        if rollback.exists():
            rollback.replace(paths.database)
        raise
    finally:
        if temporary.exists():
            temporary.unlink()
    if rollback.exists():
        rollback.unlink()


def reset_demo_database(paths: RuntimePaths) -> Path | None:
    """Back up and remove the database so the next launch creates a clean schema."""
    if not paths.database.exists():
        return None
    backup = backup_database(paths)
    paths.database.unlink()
    for suffix in ("-shm", "-wal"):
        sidecar = Path(f"{paths.database}{suffix}")
        if sidecar.exists():
            sidecar.unlink()
    return backup


def runtime_diagnostics(paths: RuntimePaths) -> str:
    payload = {
        "application_data": str(paths.root),
        "database_exists": paths.database.is_file(),
        "knowledge_state_exists": paths.knowledge_state.is_file(),
        "logs_directory_exists": paths.logs.is_dir(),
        "backup_count": len(list(paths.backups.glob("*.sqlite3")))
        if paths.backups.is_dir()
        else 0,
    }
    if paths.database.is_file():
        try:
            _verify_sqlite_database(paths.database)
            payload["database_integrity"] = "ok"
        except ValueError:
            payload["database_integrity"] = "failed"
    else:
        payload["database_integrity"] = "not_created"
    return json.dumps(payload, indent=2)
