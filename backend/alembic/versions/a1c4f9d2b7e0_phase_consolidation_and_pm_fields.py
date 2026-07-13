"""Phase vocabulary consolidation + project-management fields.

Per Gregory 2026-07-14:
- project_phase collapses to exactly five values: concept,
  ongoing-development, pilot-test, live, handover. Existing rows remap
  discovery->concept, build->ongoing-development, pilot->pilot-test,
  retired->handover.
- New Project columns: date_commenced, expected_finish_date,
  percent_complete, uses_process_automation, uses_ai (the last two are
  custom-edition portfolio metrics: how many projects automate processes /
  use AI).

Postgres cannot remove values from an existing enum type, so the phase
change is the rename-old/create-new/USING-cast/drop-old dance.

Revision ID: a1c4f9d2b7e0
Revises: 3f35c1d25e2e
Create Date: 2026-07-14
"""

import sqlalchemy as sa
from alembic import op

revision = "a1c4f9d2b7e0"
down_revision = "3f35c1d25e2e"
branch_labels = None
depends_on = None

_NEW_VALUES = ("concept", "ongoing-development", "pilot-test", "live", "handover")
_OLD_VALUES = ("concept", "discovery", "build", "pilot", "live", "handover", "retired")

_UPGRADE_CASE = """
    CASE phase::text
        WHEN 'discovery' THEN 'concept'
        WHEN 'build' THEN 'ongoing-development'
        WHEN 'pilot' THEN 'pilot-test'
        WHEN 'retired' THEN 'handover'
        ELSE phase::text
    END::project_phase
"""

# Lossy in reverse (concept could have been discovery, etc.) - map to the
# closest old value.
_DOWNGRADE_CASE = """
    CASE phase::text
        WHEN 'ongoing-development' THEN 'build'
        WHEN 'pilot-test' THEN 'pilot'
        ELSE phase::text
    END::project_phase
"""


def _swap_phase_enum(new_values: tuple[str, ...], using_case: str) -> None:
    op.execute("ALTER TYPE project_phase RENAME TO project_phase_old")
    quoted = ", ".join(f"'{v}'" for v in new_values)
    op.execute(f"CREATE TYPE project_phase AS ENUM ({quoted})")
    op.execute(
        f"ALTER TABLE projects ALTER COLUMN phase TYPE project_phase USING {using_case}"
    )
    op.execute("DROP TYPE project_phase_old")


def upgrade() -> None:
    _swap_phase_enum(_NEW_VALUES, _UPGRADE_CASE)

    op.add_column("projects", sa.Column("date_commenced", sa.Date(), nullable=True))
    op.add_column("projects", sa.Column("expected_finish_date", sa.Date(), nullable=True))
    op.add_column("projects", sa.Column("percent_complete", sa.Integer(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("uses_process_automation", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "projects",
        sa.Column("uses_ai", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_check_constraint(
        "ck_projects_percent_complete_range",
        "projects",
        "percent_complete IS NULL OR (percent_complete >= 0 AND percent_complete <= 100)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_projects_percent_complete_range", "projects")
    op.drop_column("projects", "uses_ai")
    op.drop_column("projects", "uses_process_automation")
    op.drop_column("projects", "percent_complete")
    op.drop_column("projects", "expected_finish_date")
    op.drop_column("projects", "date_commenced")

    _swap_phase_enum(_OLD_VALUES, _DOWNGRADE_CASE)
