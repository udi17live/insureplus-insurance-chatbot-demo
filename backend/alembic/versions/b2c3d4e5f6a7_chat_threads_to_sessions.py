"""rename chat_threads to chat_sessions and foundry_thread_id to last_response_id

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the table
    op.rename_table('chat_threads', 'chat_sessions')

    # Rename the column and make it nullable (new sessions start with no response ID)
    op.alter_column('chat_sessions', 'foundry_thread_id',
                    new_column_name='last_response_id',
                    existing_type=sa.String(length=255),
                    nullable=True)

    # Update FK constraints on dependent tables to point to chat_sessions
    op.drop_constraint('policy_creation_states_thread_id_fkey', 'policy_creation_states', type_='foreignkey')
    op.create_foreign_key(
        'policy_creation_states_thread_id_fkey',
        'policy_creation_states', 'chat_sessions',
        ['thread_id'], ['id']
    )

    op.drop_constraint('tool_call_logs_thread_id_fkey', 'tool_call_logs', type_='foreignkey')
    op.create_foreign_key(
        'tool_call_logs_thread_id_fkey',
        'tool_call_logs', 'chat_sessions',
        ['thread_id'], ['id']
    )

    op.drop_constraint('conversation_analytics_thread_id_fkey', 'conversation_analytics', type_='foreignkey')
    op.create_foreign_key(
        'conversation_analytics_thread_id_fkey',
        'conversation_analytics', 'chat_sessions',
        ['thread_id'], ['id']
    )


def downgrade() -> None:
    # Restore FK constraints to chat_threads
    op.drop_constraint('conversation_analytics_thread_id_fkey', 'conversation_analytics', type_='foreignkey')
    op.create_foreign_key(
        'conversation_analytics_thread_id_fkey',
        'conversation_analytics', 'chat_threads',
        ['thread_id'], ['id']
    )

    op.drop_constraint('tool_call_logs_thread_id_fkey', 'tool_call_logs', type_='foreignkey')
    op.create_foreign_key(
        'tool_call_logs_thread_id_fkey',
        'tool_call_logs', 'chat_threads',
        ['thread_id'], ['id']
    )

    op.drop_constraint('policy_creation_states_thread_id_fkey', 'policy_creation_states', type_='foreignkey')
    op.create_foreign_key(
        'policy_creation_states_thread_id_fkey',
        'policy_creation_states', 'chat_threads',
        ['thread_id'], ['id']
    )

    # Restore column name and NOT NULL constraint
    op.alter_column('chat_sessions', 'last_response_id',
                    new_column_name='foundry_thread_id',
                    existing_type=sa.String(length=255),
                    nullable=False)

    # Rename the table back
    op.rename_table('chat_sessions', 'chat_threads')
