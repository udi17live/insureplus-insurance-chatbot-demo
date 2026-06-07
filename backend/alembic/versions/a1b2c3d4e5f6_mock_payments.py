"""replace stripe columns with mock payment_reference

Revision ID: a1b2c3d4e5f6
Revises: 3b3865cbe11c
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3b3865cbe11c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('payments_stripe_payment_intent_id_key', 'payments', type_='unique')
    op.drop_column('payments', 'stripe_payment_intent_id')
    op.drop_column('payments', 'stripe_metadata')
    op.add_column('payments', sa.Column('payment_reference', sa.String(length=255), nullable=False, server_default='LEGACY'))
    op.add_column('payments', sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.create_unique_constraint('payments_payment_reference_key', 'payments', ['payment_reference'])
    op.alter_column('payments', 'payment_reference', server_default=None)
    op.alter_column('payments', 'metadata', server_default=None)


def downgrade() -> None:
    op.drop_constraint('payments_payment_reference_key', 'payments', type_='unique')
    op.drop_column('payments', 'payment_reference')
    op.drop_column('payments', 'metadata')
    op.add_column('payments', sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=False, server_default='LEGACY'))
    op.add_column('payments', sa.Column('stripe_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.create_unique_constraint('payments_stripe_payment_intent_id_key', 'payments', ['stripe_payment_intent_id'])
    op.alter_column('payments', 'stripe_payment_intent_id', server_default=None)
    op.alter_column('payments', 'stripe_metadata', server_default=None)
