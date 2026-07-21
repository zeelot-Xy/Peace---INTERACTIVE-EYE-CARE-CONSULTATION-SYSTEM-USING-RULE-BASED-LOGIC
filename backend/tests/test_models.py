from sqlalchemy import inspect, text

from app.extensions import db


def test_phase_two_schema_and_sqlite_foreign_keys(app):
    expected = {
        "application_events",
        "audit_logs",
        "consultation_responses",
        "consultation_sessions",
        "refresh_tokens",
        "reports",
        "token_revocations",
        "users",
    }
    with app.app_context():
        assert expected.issubset(set(inspect(db.engine).get_table_names()))
        assert db.session.execute(text("PRAGMA foreign_keys")).scalar() == 1
