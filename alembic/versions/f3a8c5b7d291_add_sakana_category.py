"""add sakana_category + sakana.category_id

Revision ID: f3a8c5b7d291
Revises: e2b9c4f1a7d3
Create Date: 2026-05-16 17:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a8c5b7d291'
down_revision: Union[str, Sequence[str], None] = 'e2b9c4f1a7d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sakana_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_sakana_category_slug'),
        'sakana_category',
        ['slug'],
        unique=True,
    )

    # sakana table is empty in prod, so we can add NOT NULL without backfill.
    op.add_column(
        'sakana',
        sa.Column('category_id', sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        'fk_sakana_category_id',
        'sakana',
        'sakana_category',
        ['category_id'],
        ['id'],
    )
    op.create_index(
        op.f('ix_sakana_category_id'),
        'sakana',
        ['category_id'],
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_sakana_category_id'), table_name='sakana')
    op.drop_constraint('fk_sakana_category_id', 'sakana', type_='foreignkey')
    op.drop_column('sakana', 'category_id')
    op.drop_index(op.f('ix_sakana_category_slug'), table_name='sakana_category')
    op.drop_table('sakana_category')
