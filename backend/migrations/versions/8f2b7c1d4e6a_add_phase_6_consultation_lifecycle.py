"""add phase 6 consultation lifecycle

Revision ID: 8f2b7c1d4e6a
Revises: 6dcb34974863
Create Date: 2026-07-25
"""

import sqlalchemy as sa
from alembic import op


revision = "8f2b7c1d4e6a"
down_revision = "6dcb34974863"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("consultation_sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("knowledge_package_id", sa.String(length=80)))
        batch_op.add_column(sa.Column("knowledge_fingerprint", sa.String(length=64)))
        batch_op.add_column(
            sa.Column("revision", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column(
                "skipped_question_ids",
                sa.JSON(),
                nullable=False,
                server_default="[]",
            )
        )
        batch_op.add_column(sa.Column("result_snapshot", sa.JSON()))
        batch_op.add_column(sa.Column("cancelled_at", sa.DateTime(timezone=True)))

    with op.batch_alter_table("consultation_responses", schema=None) as batch_op:
        batch_op.drop_index("ix_response_consultation_question")
        batch_op.add_column(sa.Column("fact_id", sa.String(length=80)))
        batch_op.create_index(
            "ix_response_consultation_fact",
            ["consultation_id", "fact_id"],
            unique=False,
        )
        batch_op.create_unique_constraint(
            "uq_response_consultation_question",
            ["consultation_id", "question_id"],
        )


def downgrade():
    with op.batch_alter_table("consultation_responses", schema=None) as batch_op:
        batch_op.drop_constraint("uq_response_consultation_question", type_="unique")
        batch_op.drop_index("ix_response_consultation_fact")
        batch_op.drop_column("fact_id")
        batch_op.create_index(
            "ix_response_consultation_question",
            ["consultation_id", "question_id"],
            unique=False,
        )

    with op.batch_alter_table("consultation_sessions", schema=None) as batch_op:
        batch_op.drop_column("cancelled_at")
        batch_op.drop_column("result_snapshot")
        batch_op.drop_column("skipped_question_ids")
        batch_op.drop_column("revision")
        batch_op.drop_column("knowledge_fingerprint")
        batch_op.drop_column("knowledge_package_id")
