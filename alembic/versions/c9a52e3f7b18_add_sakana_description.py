"""add description to sakana

Revision ID: c9a52e3f7b18
Revises: b8e4f1c92d57
Create Date: 2026-05-07 09:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9a52e3f7b18'
down_revision: Union[str, Sequence[str], None] = 'b8e4f1c92d57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sakana', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('sakana', 'description')
