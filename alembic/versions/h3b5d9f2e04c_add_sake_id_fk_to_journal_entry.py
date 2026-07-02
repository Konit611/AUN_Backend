"""add sake_id fk to journal_entry

Revision ID: h3b5d9f2e04c
Revises: g2a4c8e1f93b
Create Date: 2026-07-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'h3b5d9f2e04c'
down_revision: Union[str, Sequence[str], None] = 'g2a4c8e1f93b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'journal_entry',
        sa.Column('sake_id', sa.String(), nullable=True),
    )
    op.create_index(
        op.f('ix_journal_entry_sake_id'), 'journal_entry', ['sake_id'],
    )
    op.create_foreign_key(
        'fk_journal_entry_sake_id_sake',
        'journal_entry', 'sake',
        ['sake_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_journal_entry_sake_id_sake', 'journal_entry', type_='foreignkey',
    )
    op.drop_index(op.f('ix_journal_entry_sake_id'), table_name='journal_entry')
    op.drop_column('journal_entry', 'sake_id')
