"""add body_json, body_html, is_draft to article and pairing_item

Revision ID: b8e4f1c92d57
Revises: a8e3b7c4f291
Create Date: 2026-05-06 22:00:00.000000

Lays the groundwork for the BlockNote editor migration.

article:
  + body_json   (JSONB, nullable)   — BlockNote PartialBlock[] state
  + body_html   (TEXT, nullable)    — pre-rendered HTML for SSR/SEO
  + is_draft    (BOOL, default false, indexed)

pairing_item:
  + body_json   (JSONB, nullable)
  + body_html   (TEXT, nullable)
  + is_draft    (BOOL, default false, indexed)
  ~ body / why_it_works / how_to_enjoy  → made nullable so the new wizard
    can collapse all narrative into body_html without keeping the old
    four-section split.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = 'b8e4f1c92d57'
down_revision: Union[str, Sequence[str], None] = 'a8e3b7c4f291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('article', sa.Column('body_json', JSONB(), nullable=True))
    op.add_column('article', sa.Column('body_html', sa.Text(), nullable=True))
    op.add_column(
        'article',
        sa.Column(
            'is_draft', sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.create_index(op.f('ix_article_is_draft'), 'article', ['is_draft'], unique=False)

    op.add_column('pairing_item', sa.Column('body_json', JSONB(), nullable=True))
    op.add_column('pairing_item', sa.Column('body_html', sa.Text(), nullable=True))
    op.add_column(
        'pairing_item',
        sa.Column(
            'is_draft', sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.create_index(
        op.f('ix_pairing_item_is_draft'), 'pairing_item', ['is_draft'], unique=False
    )

    op.alter_column('pairing_item', 'body', existing_type=sa.String(), nullable=True)
    op.alter_column(
        'pairing_item', 'why_it_works', existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        'pairing_item', 'how_to_enjoy', existing_type=sa.String(), nullable=True
    )
    op.alter_column('pairing_item', 'sake_id', existing_type=sa.String(), nullable=True)
    op.alter_column('pairing_item', 'sakana_id', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    op.alter_column(
        'pairing_item', 'sakana_id', existing_type=sa.String(), nullable=False
    )
    op.alter_column(
        'pairing_item', 'sake_id', existing_type=sa.String(), nullable=False
    )
    op.alter_column(
        'pairing_item', 'how_to_enjoy', existing_type=sa.String(), nullable=False
    )
    op.alter_column(
        'pairing_item', 'why_it_works', existing_type=sa.String(), nullable=False
    )
    op.alter_column('pairing_item', 'body', existing_type=sa.String(), nullable=False)

    op.drop_index(op.f('ix_pairing_item_is_draft'), table_name='pairing_item')
    op.drop_column('pairing_item', 'is_draft')
    op.drop_column('pairing_item', 'body_html')
    op.drop_column('pairing_item', 'body_json')

    op.drop_index(op.f('ix_article_is_draft'), table_name='article')
    op.drop_column('article', 'is_draft')
    op.drop_column('article', 'body_html')
    op.drop_column('article', 'body_json')
