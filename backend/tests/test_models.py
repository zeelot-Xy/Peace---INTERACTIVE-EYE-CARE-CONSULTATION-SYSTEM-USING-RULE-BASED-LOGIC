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


def test_phase_six_consultation_constraints(app):
    with app.app_context():
        inspector = inspect(db.engine)
        session_columns = {
            column["name"]
            for column in inspector.get_columns("consultation_sessions")
        }
        response_columns = {
            column["name"]
            for column in inspector.get_columns("consultation_responses")
        }
        unique_constraints = {
            constraint["name"]
            for constraint in inspector.get_unique_constraints(
                "consultation_responses"
            )
        }

    assert {
        "knowledge_package_id",
        "knowledge_fingerprint",
        "revision",
        "skipped_question_ids",
        "result_snapshot",
        "cancelled_at",
    } <= session_columns
    assert "fact_id" in response_columns
    assert "uq_response_consultation_question" in unique_constraints


def test_phase_nine_report_columns_are_immutable_artifacts(app):
    with app.app_context():
        inspector = inspect(db.engine)
        columns = {
            column["name"] for column in inspector.get_columns("reports")
        }
        unique_constraints = {
            constraint["name"]
            for constraint in inspector.get_unique_constraints("reports")
        }

    assert {
        "filename",
        "content_type",
        "pdf_sha256",
        "pdf_data",
        "snapshot",
    } <= columns
    assert "uq_reports_pdf_sha256" in unique_constraints
