"""rename recipe → sakana (table, columns, indexes, fk constraint)

Revision ID: f7d2a1c93e58
Revises: e1c7f4d8a9b3
Create Date: 2026-05-06 12:00:00.000000

Renames:
  - table `recipe`              → `sakana`
  - table `sake_recipe`         → `sake_sakana`
  - column `sake_recipe.recipe_id`  → `sake_sakana.sakana_id`
  - column `pairing_item.recipe_id` → `pairing_item.sakana_id`
  - index `ix_recipe_name`            → `ix_sakana_name`
  - index `ix_pairing_item_recipe_id` → `ix_pairing_item_sakana_id`
  - fk    `fk_pairing_item_recipe_id` → `fk_pairing_item_sakana_id`
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'f7d2a1c93e58'
down_revision: Union[str, Sequence[str], None] = 'e1c7f4d8a9b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('recipe', 'sakana')
    op.execute('ALTER INDEX ix_recipe_name RENAME TO ix_sakana_name')

    op.alter_column('sake_recipe', 'recipe_id', new_column_name='sakana_id')
    op.rename_table('sake_recipe', 'sake_sakana')

    op.alter_column('pairing_item', 'recipe_id', new_column_name='sakana_id')
    op.execute('ALTER INDEX ix_pairing_item_recipe_id RENAME TO ix_pairing_item_sakana_id')
    op.execute(
        'ALTER TABLE pairing_item '
        'RENAME CONSTRAINT fk_pairing_item_recipe_id TO fk_pairing_item_sakana_id'
    )

    # Auto-generated PK/FK names from the original sake_recipe table
    op.execute('ALTER INDEX sake_recipe_pkey RENAME TO sake_sakana_pkey')
    op.execute(
        'ALTER TABLE sake_sakana '
        'RENAME CONSTRAINT sake_recipe_recipe_id_fkey TO sake_sakana_sakana_id_fkey'
    )
    op.execute(
        'ALTER TABLE sake_sakana '
        'RENAME CONSTRAINT sake_recipe_sake_id_fkey TO sake_sakana_sake_id_fkey'
    )


def downgrade() -> None:
    op.execute(
        'ALTER TABLE sake_sakana '
        'RENAME CONSTRAINT sake_sakana_sake_id_fkey TO sake_recipe_sake_id_fkey'
    )
    op.execute(
        'ALTER TABLE sake_sakana '
        'RENAME CONSTRAINT sake_sakana_sakana_id_fkey TO sake_recipe_recipe_id_fkey'
    )
    op.execute('ALTER INDEX sake_sakana_pkey RENAME TO sake_recipe_pkey')

    op.execute(
        'ALTER TABLE pairing_item '
        'RENAME CONSTRAINT fk_pairing_item_sakana_id TO fk_pairing_item_recipe_id'
    )
    op.execute('ALTER INDEX ix_pairing_item_sakana_id RENAME TO ix_pairing_item_recipe_id')
    op.alter_column('pairing_item', 'sakana_id', new_column_name='recipe_id')

    op.rename_table('sake_sakana', 'sake_recipe')
    op.alter_column('sake_recipe', 'sakana_id', new_column_name='recipe_id')

    op.execute('ALTER INDEX ix_sakana_name RENAME TO ix_recipe_name')
    op.rename_table('sakana', 'recipe')
