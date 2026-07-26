import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path

import click
from flask import Flask, current_app

from app.extensions import db
from app.inference import FactValidationError, InferenceConfigurationError
from app.models import ConsultationSession, RefreshToken, TokenRevocation, User
from app.services.audit_service import record_audit
from app.services.auth_service import normalize_email, validate_password


def register_commands(app: Flask) -> None:
    def sqlite_database_path() -> Path:
        database = db.engine.url.database
        if not database or db.engine.url.get_backend_name() != "sqlite":
            raise click.ClickException(
                "This maintenance command supports SQLite databases only."
            )
        return Path(database).resolve()

    def verified_sqlite_source(path: Path) -> sqlite3.Connection:
        connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        result = connection.execute("PRAGMA quick_check").fetchone()
        if not result or result[0] != "ok":
            connection.close()
            raise click.ClickException("The SQLite source failed its integrity check.")
        return connection

    @app.cli.command("inference-evaluate")
    @click.option(
        "--facts-file",
        required=True,
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
        help="Path to a local JSON object containing non-sensitive demonstration facts.",
    )
    @click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON.")
    def inference_evaluate(facts_file: Path, as_json: bool) -> None:
        """Evaluate non-sensitive demonstration facts against the active package."""
        try:
            facts = json.loads(facts_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise click.ClickException(f"Unable to read facts JSON: {error}") from error
        try:
            result = current_app.extensions["inference"].evaluate(
                current_app.extensions["knowledge"].get_active(), facts
            )
        except FactValidationError as error:
            if as_json:
                click.echo(json.dumps(error.to_dict(), indent=2))
                raise click.exceptions.Exit(1) from error
            details = "; ".join(f"{issue.fact_id}: {issue.code}" for issue in error.issues)
            raise click.ClickException(f"Invalid facts: {details}") from error
        except InferenceConfigurationError as error:
            raise click.ClickException(str(error)) from error
        payload = result.to_dict()
        if as_json:
            click.echo(json.dumps(payload, indent=2))
        else:
            risk = payload["overall_risk"]
            risk_label = risk["label"] if risk else "No matched risk level"
            click.echo(
                f"Outcome: {payload['outcome_state']} ({payload['completeness_state']}); "
                f"risk: {risk_label}; matched rules: {len(payload['matched_rules'])}"
            )

    @app.cli.command("knowledge-status")
    @click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON.")
    def knowledge_status(as_json: bool) -> None:
        """Show the configured active knowledge package."""
        status = current_app.extensions["knowledge"].get_status()
        if as_json:
            click.echo(json.dumps(status, indent=2))
        else:
            click.echo(
                f"Active package: {status['package_id']} "
                f"(content {status['content_version']}, {status['manifest_status']})"
            )

    @app.cli.command("knowledge-validate")
    @click.argument("package", required=False, type=click.Path(path_type=Path))
    @click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON.")
    def knowledge_validate(package: Path | None, as_json: bool) -> None:
        """Validate a package without changing the active snapshot."""
        manager = current_app.extensions["knowledge"]
        candidate = package or (
            Path(current_app.config["KNOWLEDGE_PACKAGES_DIR"])
            / current_app.config["KNOWLEDGE_ACTIVE_PACKAGE"]
        )
        report = manager.validate(candidate)
        if as_json:
            click.echo(json.dumps(report.to_dict(), indent=2))
        elif report.valid:
            click.echo(f"Knowledge package is valid: {candidate}")
        else:
            for issue in report.issues:
                click.echo(f"{issue.code}: {issue.location}: {issue.message}")
        if not report.valid:
            raise click.exceptions.Exit(1)

    @app.cli.command("bootstrap-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt="Full name")
    @click.password_option(confirmation_prompt=True)
    def bootstrap_admin(email: str, name: str, password: str) -> None:
        """Create the first administrator without default credentials."""
        normalized = normalize_email(email)
        if db.session.scalar(db.select(User).where(User.email == normalized)):
            raise click.ClickException(
                "An account with that email already exists; no changes made."
            )
        validate_password(password)
        user = User(email=normalized, full_name=name.strip(), role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        record_audit(
            "admin.bootstrap", actor_user_id=user.id, resource_type="user", resource_id=user.id
        )
        db.session.commit()
        click.echo(f"Administrator created for {normalized}.")

    @app.cli.command("database-backup")
    @click.option(
        "--output",
        type=click.Path(dir_okay=False, path_type=Path),
        help="Destination .sqlite file. Defaults to instance/backups.",
    )
    def database_backup(output: Path | None) -> None:
        """Create a transactionally consistent SQLite backup."""
        source_path = sqlite_database_path()
        destination = output or (
            Path(current_app.instance_path)
            / "backups"
            / f"eye-care-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.sqlite"
        )
        destination = destination.resolve()
        if destination == source_path:
            raise click.ClickException("Backup destination must differ from the live database.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise click.ClickException("Backup destination already exists.")
        with (
            closing(sqlite3.connect(source_path)) as source,
            closing(sqlite3.connect(destination)) as target,
        ):
            source.backup(target)
        with closing(verified_sqlite_source(destination)):
            pass
        click.echo(f"Verified backup created: {destination}")

    @app.cli.command("database-restore")
    @click.argument(
        "backup",
        type=click.Path(exists=True, dir_okay=False, path_type=Path),
    )
    @click.option(
        "--confirm",
        is_flag=True,
        help="Required acknowledgement that the live database will be replaced.",
    )
    def database_restore(backup: Path, confirm: bool) -> None:
        """Restore a verified SQLite backup after explicit confirmation."""
        if not confirm:
            raise click.ClickException("Pass --confirm to restore a database backup.")
        source_path = backup.resolve()
        live_path = sqlite_database_path()
        if source_path == live_path:
            raise click.ClickException("Backup source must differ from the live database.")
        with closing(verified_sqlite_source(source_path)) as source:
            db.session.remove()
            db.engine.dispose()
            live_path.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(live_path)) as target:
                source.backup(target)
        with closing(verified_sqlite_source(live_path)):
            pass
        click.echo(f"Verified database restored from: {source_path}")

    @app.cli.command("privacy-maintenance")
    @click.option(
        "--apply",
        is_flag=True,
        help="Apply the retention purge. Without this flag the command is a dry run.",
    )
    def privacy_maintenance(apply: bool) -> None:
        """Preview or purge records beyond the documented retention windows."""
        now = datetime.now(UTC)
        abandoned_before = now - timedelta(
            days=current_app.config["RETENTION_ABANDONED_DAYS"]
        )
        completed_before = now - timedelta(
            days=current_app.config["RETENTION_COMPLETED_DAYS"]
        )
        token_before = now - timedelta(days=current_app.config["RETENTION_TOKEN_DAYS"])
        abandoned_filter = (
            ConsultationSession.status.in_(("in_progress", "cancelled")),
            ConsultationSession.updated_at < abandoned_before,
        )
        completed_filter = (
            ConsultationSession.status == "completed",
            ConsultationSession.completed_at < completed_before,
        )
        refresh_filter = RefreshToken.expires_at < token_before
        revocation_filter = TokenRevocation.expires_at < token_before
        counts = {
            "abandoned_consultations": db.session.scalar(
                db.select(db.func.count(ConsultationSession.id)).where(*abandoned_filter)
            )
            or 0,
            "completed_consultations": db.session.scalar(
                db.select(db.func.count(ConsultationSession.id)).where(*completed_filter)
            )
            or 0,
            "refresh_tokens": db.session.scalar(
                db.select(db.func.count(RefreshToken.id)).where(refresh_filter)
            )
            or 0,
            "token_revocations": db.session.scalar(
                db.select(db.func.count(TokenRevocation.id)).where(revocation_filter)
            )
            or 0,
        }
        if apply:
            db.session.execute(db.delete(ConsultationSession).where(*abandoned_filter))
            db.session.execute(db.delete(ConsultationSession).where(*completed_filter))
            db.session.execute(db.delete(RefreshToken).where(refresh_filter))
            db.session.execute(db.delete(TokenRevocation).where(revocation_filter))
            record_audit("privacy.retention_purge", event_data=counts)
            db.session.commit()
        click.echo(
            json.dumps(
                {
                    "mode": "applied" if apply else "dry_run",
                    "eligible": counts,
                },
                indent=2,
            )
        )

    @app.cli.command("delete-user-data")
    @click.argument("user_id")
    @click.option(
        "--confirm",
        is_flag=True,
        help="Required acknowledgement that patient data will be permanently deleted.",
    )
    def delete_user_data(user_id: str, confirm: bool) -> None:
        """Delete one patient and cascade their consultations and reports."""
        if not confirm:
            raise click.ClickException("Pass --confirm to delete patient data.")
        user = db.session.get(User, user_id)
        if user is None:
            raise click.ClickException("User was not found.")
        if user.role == "admin":
            raise click.ClickException(
                "Administrator accounts require a separate governance review."
            )
        db.session.delete(user)
        record_audit(
            "privacy.patient_deleted",
            resource_type="user",
            resource_id=user_id,
        )
        db.session.commit()
        click.echo(f"Patient data deleted for user ID: {user_id}")
