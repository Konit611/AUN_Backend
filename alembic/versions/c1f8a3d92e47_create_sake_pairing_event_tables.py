"""create sake, flavor, recipe, pairing_guide, event tables

Revision ID: c1f8a3d92e47
Revises: daf951727416
Create Date: 2026-04-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'c1f8a3d92e47'
down_revision: Union[str, Sequence[str], None] = 'daf951727416'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sake',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('brewery', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('region', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('rice', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('polishing', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('serving_temperature', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('serving_season', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('persona_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sake_persona_code'), 'sake', ['persona_code'], unique=False)

    op.create_table(
        'flavor',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_flavor_label'), 'flavor', ['label'], unique=True)

    op.create_table(
        'sake_flavor',
        sa.Column('sake_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('flavor_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['flavor_id'], ['flavor.id'], ),
        sa.ForeignKeyConstraint(['sake_id'], ['sake.id'], ),
        sa.PrimaryKeyConstraint('sake_id', 'flavor_id'),
    )

    op.create_table(
        'recipe',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('emoji', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('image_placeholder', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recipe_name'), 'recipe', ['name'], unique=True)

    op.create_table(
        'sake_recipe',
        sa.Column('sake_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('recipe_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
        sa.ForeignKeyConstraint(['sake_id'], ['sake.id'], ),
        sa.PrimaryKeyConstraint('sake_id', 'recipe_id'),
    )

    op.create_table(
        'event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name_ja', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description_ja', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'pairing_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_pairing_category_slug'), 'pairing_category', ['slug'], unique=True)

    op.create_table(
        'pairing_item',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('emoji', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('food_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sake_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sake_brewery', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sake_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('temperature', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('season', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('body', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('why_it_works', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('how_to_enjoy', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('food_image', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('sake_image', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('sake_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('persona_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['pairing_category.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
        sa.ForeignKeyConstraint(['sake_id'], ['sake.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_pairing_item_category_id'), 'pairing_item', ['category_id'], unique=False)
    op.create_index(op.f('ix_pairing_item_event_id'), 'pairing_item', ['event_id'], unique=False)
    op.create_index(op.f('ix_pairing_item_persona_code'), 'pairing_item', ['persona_code'], unique=False)
    op.create_index(op.f('ix_pairing_item_sake_id'), 'pairing_item', ['sake_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_pairing_item_sake_id'), table_name='pairing_item')
    op.drop_index(op.f('ix_pairing_item_persona_code'), table_name='pairing_item')
    op.drop_index(op.f('ix_pairing_item_event_id'), table_name='pairing_item')
    op.drop_index(op.f('ix_pairing_item_category_id'), table_name='pairing_item')
    op.drop_table('pairing_item')
    op.drop_index(op.f('ix_pairing_category_slug'), table_name='pairing_category')
    op.drop_table('pairing_category')
    op.drop_table('event')
    op.drop_table('sake_recipe')
    op.drop_index(op.f('ix_recipe_name'), table_name='recipe')
    op.drop_table('recipe')
    op.drop_table('sake_flavor')
    op.drop_index(op.f('ix_flavor_label'), table_name='flavor')
    op.drop_table('flavor')
    op.drop_index(op.f('ix_sake_persona_code'), table_name='sake')
    op.drop_table('sake')
