"""add phase 8 knowledge versions

Revision ID: 4c8a9d2e7f10
Revises: 8f2b7c1d4e6a
Create Date: 2026-07-26
"""

import sqlalchemy as sa
from alembic import op


revision = "4c8a9d2e7f10"
down_revision = "8f2b7c1d4e6a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "knowledge_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=80)),
        sa.Column("schema_version", sa.String(length=30)),
        sa.Column("content_version", sa.String(length=30)),
        sa.Column("fingerprint", sa.String(length=64)),
        sa.Column("title", sa.String(length=200)),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024)),
        sa.Column("validation_report", sa.JSON(), nullable=False),
        sa.Column("diff_summary", sa.JSON()),
        sa.Column("uploaded_by_user_id", sa.String(length=36)),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("retired_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(
            ["uploaded_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "content_version",
        "fingerprint",
        "is_active",
        "package_id",
        "status",
        "uploaded_by_user_id",
    ):
        op.create_index(
            f"ix_knowledge_versions_{column}",
            "knowledge_versions",
            [column],
            unique=column in {"fingerprint", "package_id"},
        )


def downgrade():
    op.drop_table("knowledge_versions")
