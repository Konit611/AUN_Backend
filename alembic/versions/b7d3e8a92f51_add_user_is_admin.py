"""add is_admin to user

Revision ID: b7d3e8a92f51
Revises: a4f2e9c81b3d
Create Date: 2026-05-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7d3e8a92f51'
down_revision: Union[str, Sequence[str], None] = 'a4f2e9c81b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column('user', 'is_admin', server_default=None)


def downgrade() -> None:
    op.drop_column('user', 'is_admin')
