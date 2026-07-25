import json
from pathlib import Path

import click
from flask import Flask, current_app

from app.extensions import db
from app.inference import FactValidationError, InferenceConfigurationError
from app.models import User
from app.services.audit_service import record_audit
from app.services.auth_service import normalize_email, validate_password


def register_commands(app: Flask) -> None:
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
