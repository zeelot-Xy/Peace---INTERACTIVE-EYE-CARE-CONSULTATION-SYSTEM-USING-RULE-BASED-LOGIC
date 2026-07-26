"""add immutable PDF reports

Revision ID: 9a1c5e7f2b40
Revises: 4c8a9d2e7f10
Create Date: 2026-07-26
"""

import sqlalchemy as sa
from alembic import op


revision = "9a1c5e7f2b40"
down_revision = "4c8a9d2e7f10"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.add_column(sa.Column("filename", sa.String(length=255)))
        batch_op.add_column(
            sa.Column(
                "content_type",
                sa.String(length=80),
                nullable=False,
                server_default="application/pdf",
            )
        )
        batch_op.add_column(sa.Column("pdf_sha256", sa.String(length=64)))
        batch_op.add_column(sa.Column("pdf_data", sa.LargeBinary()))
        batch_op.create_unique_constraint(
            "uq_reports_pdf_sha256", ["pdf_sha256"]
        )

    # Phase 9 is the first phase that creates reports, so deployed rows are not
    # expected. Nullable staging keeps SQLite batch migration deterministic.
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.alter_column("filename", nullable=False)
        batch_op.alter_column("pdf_sha256", nullable=False)
        batch_op.alter_column("pdf_data", nullable=False)


def downgrade():
    with op.batch_alter_table("reports", schema=None) as batch_op:
        batch_op.drop_constraint("uq_reports_pdf_sha256", type_="unique")
        batch_op.drop_column("pdf_data")
        batch_op.drop_column("pdf_sha256")
        batch_op.drop_column("content_type")
        batch_op.drop_column("filename")
