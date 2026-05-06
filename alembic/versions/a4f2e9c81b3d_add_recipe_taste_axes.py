"""add 6 taste axes to recipe table

Revision ID: a4f2e9c81b3d
Revises: c1f8a3d92e47
Create Date: 2026-05-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a4f2e9c81b3d'
down_revision: Union[str, Sequence[str], None] = 'c1f8a3d92e47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AXES = [
    ("sweetness", 0.5),
    ("umami", 0.5),
    ("acidity", 0.3),
    ("fat", 0.3),
    ("aroma", 0.4),
    ("saltiness", 0.3),
]


def upgrade() -> None:
    """Upgrade schema."""
    for name, default in AXES:
        op.add_column(
            'recipe',
            sa.Column(name, sa.Float(), nullable=False, server_default=str(default)),
        )
    # drop server_default after backfill so app-level defaults take over
    for name, _ in AXES:
        op.alter_column('recipe', name, server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    for name, _ in reversed(AXES):
        op.drop_column('recipe', name)
