"""extend user with profile fields, age/consent, and OAuth-friendly nullable password

Revision ID: a8e3b7c4f291
Revises: f7d2a1c93e58
Create Date: 2026-05-06 14:00:00.000000

Adds:
  - birthdate                       (DATE, nullable — required for new signups via API)
  - terms_accepted_at               (TIMESTAMP, nullable)
  - privacy_accepted_at             (TIMESTAMP, nullable)
  - display_name / bio / avatar_url (profile)
  - persona_code                    (4-char diagnosis result, indexed)
  - password_changed_at             (audit hint for change-password)
Makes:
  - hashed_password                 nullable (so future OAuth-only users
                                    can exist without a password)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a8e3b7c4f291'
down_revision: Union[str, Sequence[str], None] = 'f7d2a1c93e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('user', 'hashed_password', existing_type=sa.String(), nullable=True)

    op.add_column('user', sa.Column('birthdate', sa.Date(), nullable=True))
    op.add_column('user', sa.Column('terms_accepted_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('privacy_accepted_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('display_name', sa.String(), nullable=True))
    op.add_column('user', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('user', sa.Column('persona_code', sa.String(length=4), nullable=True))
    op.add_column('user', sa.Column('password_changed_at', sa.DateTime(), nullable=True))

    op.create_index(op.f('ix_user_persona_code'), 'user', ['persona_code'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_persona_code'), table_name='user')
    op.drop_column('user', 'password_changed_at')
    op.drop_column('user', 'persona_code')
    op.drop_column('user', 'avatar_url')
    op.drop_column('user', 'bio')
    op.drop_column('user', 'display_name')
    op.drop_column('user', 'privacy_accepted_at')
    op.drop_column('user', 'terms_accepted_at')
    op.drop_column('user', 'birthdate')

    op.alter_column('user', 'hashed_password', existing_type=sa.String(), nullable=False)
