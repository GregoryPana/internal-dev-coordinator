"""seed bootstrap admin

Revision ID: c3e9ed123901
Revises: 2bc99a0c5cc8
Create Date: 2026-07-13 13:50:47.765312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3e9ed123901'
down_revision: Union[str, None] = '2bc99a0c5cc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ADMIN_EMAIL = "gregory.panagary@cwseychelles.com"


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO people (name, email, role_type, department, active) "
            "VALUES ('Gregory Panagary', :email, 'admin', 'DTO', true) "
            "ON CONFLICT (email) DO NOTHING"
        ).bindparams(email=ADMIN_EMAIL)
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM people WHERE email = :email").bindparams(email=ADMIN_EMAIL))
