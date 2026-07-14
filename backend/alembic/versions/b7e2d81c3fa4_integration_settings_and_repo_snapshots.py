"""Integration settings (encrypted in-app credentials) + repo snapshots
(active tracking persistence), plus additive audit enum values.

Note on enums (see the standing pre-flight check): this migration only ADDS
values to existing enum types - Postgres cannot remove enum values, so the
downgrade leaves 'integration_updated' / 'integration' in place (harmless:
nothing references them after the tables are dropped).

Revision ID: b7e2d81c3fa4
Revises: a1c4f9d2b7e0
Create Date: 2026-07-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b7e2d81c3fa4"
down_revision = "a1c4f9d2b7e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE audit_action_type ADD VALUE IF NOT EXISTS 'integration_updated'")
    op.execute("ALTER TYPE audit_object_type ADD VALUE IF NOT EXISTS 'integration'")

    op.create_table(
        "integration_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("encrypted_credential", sa.Text(), nullable=True),
        sa.Column("config_json", postgresql.JSONB(), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_integration_settings_provider", "integration_settings", ["provider"], unique=True)

    op.create_table(
        "repo_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("data_json", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_repo_snapshots_project_id", "repo_snapshots", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_repo_snapshots_project_id", table_name="repo_snapshots")
    op.drop_table("repo_snapshots")
    op.drop_index("ix_integration_settings_provider", table_name="integration_settings")
    op.drop_table("integration_settings")
    # Enum values added in upgrade() cannot be removed from Postgres enums;
    # they remain, unreferenced.
