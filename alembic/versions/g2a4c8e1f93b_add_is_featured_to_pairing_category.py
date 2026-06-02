"""add is_featured to pairing_category

Revision ID: g2a4c8e1f93b
Revises: e1c7f4d8a9b3
Create Date: 2026-06-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'g2a4c8e1f93b'
down_revision: Union[str, Sequence[str], None] = 'f3a8c5b7d291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'pairing_category',
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('pairing_category', 'is_featured')
