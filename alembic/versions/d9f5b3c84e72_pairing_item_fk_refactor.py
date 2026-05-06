"""pairing_item refactor: drop denormalized fields, require sake_id + recipe_id FK, add hero_image

Revision ID: d9f5b3c84e72
Revises: c8e4a2b71d63
Create Date: 2026-05-06 00:02:00.000000

Aggressive: truncates pairing_item table since the new shape requires
recipe_id (no clean way to backfill the legacy 牛炙り entry).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd9f5b3c84e72'
down_revision: Union[str, Sequence[str], None] = 'c8e4a2b71d63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Wipe existing rows — operator will recreate via admin UI.
    op.execute("DELETE FROM pairing_item")

    # Drop denormalized columns
    op.drop_column('pairing_item', 'food_name')
    op.drop_column('pairing_item', 'sake_name')
    op.drop_column('pairing_item', 'sake_brewery')
    op.drop_column('pairing_item', 'sake_type')
    op.drop_column('pairing_item', 'food_image')
    op.drop_column('pairing_item', 'sake_image')
    op.drop_column('pairing_item', 'emoji')

    # Add new fields
    op.add_column(
        'pairing_item',
        sa.Column('recipe_id', sa.String(), nullable=False),
    )
    op.create_foreign_key(
        'fk_pairing_item_recipe_id',
        'pairing_item', 'recipe',
        ['recipe_id'], ['id'],
    )
    op.create_index(
        op.f('ix_pairing_item_recipe_id'),
        'pairing_item',
        ['recipe_id'],
        unique=False,
    )

    op.add_column(
        'pairing_item',
        sa.Column('hero_image', sa.String(), nullable=True),
    )

    # Make sake_id required
    op.alter_column('pairing_item', 'sake_id', nullable=False)


def downgrade() -> None:
    op.alter_column('pairing_item', 'sake_id', nullable=True)
    op.drop_column('pairing_item', 'hero_image')
    op.drop_index(op.f('ix_pairing_item_recipe_id'), table_name='pairing_item')
    op.drop_constraint('fk_pairing_item_recipe_id', 'pairing_item', type_='foreignkey')
    op.drop_column('pairing_item', 'recipe_id')
    op.add_column('pairing_item', sa.Column('emoji', sa.String(), nullable=False, server_default=''))
    op.add_column('pairing_item', sa.Column('sake_image', sa.String(), nullable=True))
    op.add_column('pairing_item', sa.Column('food_image', sa.String(), nullable=True))
    op.add_column('pairing_item', sa.Column('sake_type', sa.String(), nullable=False, server_default=''))
    op.add_column('pairing_item', sa.Column('sake_brewery', sa.String(), nullable=False, server_default=''))
    op.add_column('pairing_item', sa.Column('sake_name', sa.String(), nullable=False, server_default=''))
    op.add_column('pairing_item', sa.Column('food_name', sa.String(), nullable=False, server_default=''))
