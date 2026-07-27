import argparse
import contextlib
import getpass
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from types import TracebackType

from waitress import serve

from app import create_app
from app.maintenance import (
    backup_database,
    reset_demo_database,
    restore_database,
    runtime_diagnostics,
)
from app.runtime import (
    RuntimePaths,
    configure_packaged_environment,
    local_runtime_paths,
)
from app.services.auth_service import bootstrap_administrator
from app.startup import apply_database_migrations, configure_file_logging

DEFAULT_PORT = 8765


def find_available_port(preferred_port: int = DEFAULT_PORT) -> int:
    for port in range(preferred_port, min(preferred_port + 100, 65536)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
            try:
                candidate.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


class SingleInstance:
    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.handle = None

    def __enter__(self) -> "SingleInstance":
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.handle = self.lock_file.open("a+b")
            self.handle.seek(0)
            if self.handle.read(1) == b"":
                self.handle.write(b"0")
                self.handle.flush()
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            if self.handle:
                self.handle.close()
            self.handle = None
            raise RuntimeError("Eye Care Consultation is already running.") from error
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.handle:
            return
        with contextlib.suppress(OSError):
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()
        self.handle = None


def open_browser_when_ready(url: str, timeout_seconds: float = 30) -> None:
    health_url = f"{url}/api/v1/health"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except OSError:
            time.sleep(0.2)


def _paths_from_argument(data_directory: str | None) -> RuntimePaths:
    return local_runtime_paths(Path(data_directory) if data_directory else None)


def run_application(args: argparse.Namespace) -> int:
    paths = _paths_from_argument(args.data_directory)
    with SingleInstance(paths.root / "eye-care.lock"):
        config_overrides = configure_packaged_environment(paths)
        app = create_app("packaged", config_overrides)
        configure_file_logging(app, paths.logs)
        apply_database_migrations(app)
        port = find_available_port(args.port)
        url = f"http://127.0.0.1:{port}"
        app.logger.info("Starting packaged application at %s", url)
        if not args.no_browser:
            threading.Thread(
                target=open_browser_when_ready,
                args=(url,),
                daemon=True,
            ).start()
        serve(app, host="127.0.0.1", port=port, threads=4)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="EyeCareConsultation",
        description="Eye Care Consultation local application and maintenance utility.",
    )
    parser.add_argument(
        "--data-directory",
        help="Override the application data directory for support and testing.",
    )
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run", help="Start the local application.")
    run_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    run_parser.add_argument("--no-browser", action="store_true")

    backup_parser = subparsers.add_parser("backup", help="Create a verified database backup.")
    backup_parser.add_argument("--output", type=Path)

    restore_parser = subparsers.add_parser("restore", help="Restore a verified database backup.")
    restore_parser.add_argument("backup", type=Path)
    restore_parser.add_argument("--confirm", action="store_true")

    reset_parser = subparsers.add_parser(
        "reset-demo-data",
        help="Back up and reset the local demonstration database.",
    )
    reset_parser.add_argument("--confirm", action="store_true")

    subparsers.add_parser(
        "bootstrap-admin",
        help="Interactively create the first administrator.",
    )
    subparsers.add_parser("diagnostics", help="Print non-sensitive runtime diagnostics.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "run"
    paths = _paths_from_argument(args.data_directory)
    try:
        if command == "run":
            if not hasattr(args, "port"):
                args.port = DEFAULT_PORT
                args.no_browser = False
            return run_application(args)
        if command == "backup":
            destination = backup_database(paths, args.output)
            print(f"Backup created: {destination}")
            return 0
        if command == "restore":
            if not args.confirm:
                parser.error("restore requires --confirm")
            with SingleInstance(paths.root / "eye-care.lock"):
                restore_database(paths, args.backup)
            print("Backup restored successfully.")
            return 0
        if command == "reset-demo-data":
            if not args.confirm:
                parser.error("reset-demo-data requires --confirm")
            with SingleInstance(paths.root / "eye-care.lock"):
                backup = reset_demo_database(paths)
            if backup:
                print(f"Demo data reset. Safety backup: {backup}")
            else:
                print("No database exists; there was nothing to reset.")
            return 0
        if command == "bootstrap-admin":
            with SingleInstance(paths.root / "eye-care.lock"):
                config_overrides = configure_packaged_environment(paths)
                app = create_app("packaged", config_overrides)
                configure_file_logging(app, paths.logs)
                apply_database_migrations(app)
                email = input("Administrator email: ")
                name = input("Administrator full name: ")
                password = getpass.getpass("Password: ")
                confirmation = getpass.getpass("Confirm password: ")
                if password != confirmation:
                    raise ValueError("Passwords do not match.")
                with app.app_context():
                    user = bootstrap_administrator(email, name, password)
            print(f"Administrator created for {user.email}.")
            return 0
        if command == "diagnostics":
            print(runtime_diagnostics(paths))
            return 0
    except Exception as error:
        print(f"Eye Care Consultation could not continue: {error}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
