"""create article and article_category tables

Revision ID: e1c7f4d8a9b3
Revises: d9f5b3c84e72
Create Date: 2026-05-06 00:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e1c7f4d8a9b3'
down_revision: Union[str, Sequence[str], None] = 'd9f5b3c84e72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'article_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_article_category_slug'),
        'article_category',
        ['slug'],
        unique=True,
    )

    op.create_table(
        'article',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('subtitle', sa.String(), nullable=False),
        sa.Column('excerpt', sa.String(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('read_time', sa.String(), nullable=False),
        sa.Column('emoji', sa.String(), nullable=False),
        sa.Column('hero_image_url', sa.String(), nullable=True),
        sa.Column('body', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['article_category.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_article_slug'), 'article', ['slug'], unique=True)
    op.create_index(
        op.f('ix_article_category_id'),
        'article',
        ['category_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_article_category_id'), table_name='article')
    op.drop_index(op.f('ix_article_slug'), table_name='article')
    op.drop_table('article')
    op.drop_index(op.f('ix_article_category_slug'), table_name='article_category')
    op.drop_table('article_category')
