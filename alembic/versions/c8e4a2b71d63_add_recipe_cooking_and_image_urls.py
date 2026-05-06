"""add cooking fields to recipe and image_url to sake/recipe

Revision ID: c8e4a2b71d63
Revises: b7d3e8a92f51
Create Date: 2026-05-06 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c8e4a2b71d63'
down_revision: Union[str, Sequence[str], None] = 'b7d3e8a92f51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sake', sa.Column('image_url', sa.String(), nullable=True))

    op.add_column('recipe', sa.Column('food_image_url', sa.String(), nullable=True))
    op.add_column('recipe', sa.Column('ingredients', sa.JSON(), nullable=True))
    op.add_column('recipe', sa.Column('steps', sa.JSON(), nullable=True))
    op.add_column('recipe', sa.Column('prep_time_min', sa.Integer(), nullable=True))
    op.add_column('recipe', sa.Column('cook_time_min', sa.Integer(), nullable=True))
    op.add_column('recipe', sa.Column('servings', sa.Integer(), nullable=True))
    op.add_column('recipe', sa.Column('difficulty', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('recipe', 'difficulty')
    op.drop_column('recipe', 'servings')
    op.drop_column('recipe', 'cook_time_min')
    op.drop_column('recipe', 'prep_time_min')
    op.drop_column('recipe', 'steps')
    op.drop_column('recipe', 'ingredients')
    op.drop_column('recipe', 'food_image_url')
    op.drop_column('sake', 'image_url')
