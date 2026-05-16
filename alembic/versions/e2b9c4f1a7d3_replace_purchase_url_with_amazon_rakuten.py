"""replace purchase_url with amazon_url + rakuten_url

Revision ID: e2b9c4f1a7d3
Revises: d1f48b6e3a92
Create Date: 2026-05-16 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e2b9c4f1a7d3'
down_revision: Union[str, Sequence[str], None] = 'd1f48b6e3a92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sake', sa.Column('amazon_url', sa.String(), nullable=True))
    op.add_column('sake', sa.Column('rakuten_url', sa.String(), nullable=True))
    op.drop_column('sake', 'purchase_url')


def downgrade() -> None:
    op.add_column('sake', sa.Column('purchase_url', sa.String(), nullable=True))
    op.drop_column('sake', 'rakuten_url')
    op.drop_column('sake', 'amazon_url')
