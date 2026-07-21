import click
from flask import Flask

from app.extensions import db
from app.models import User
from app.services.audit_service import record_audit
from app.services.auth_service import normalize_email, validate_password


def register_commands(app: Flask) -> None:
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
