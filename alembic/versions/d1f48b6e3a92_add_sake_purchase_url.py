"""add purchase_url to sake

Revision ID: d1f48b6e3a92
Revises: c9a52e3f7b18
Create Date: 2026-05-07 11:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1f48b6e3a92'
down_revision: Union[str, Sequence[str], None] = 'c9a52e3f7b18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sake', sa.Column('purchase_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('sake', 'purchase_url')
