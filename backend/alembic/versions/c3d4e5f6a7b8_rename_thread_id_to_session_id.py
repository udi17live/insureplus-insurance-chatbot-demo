"""rename thread_id to session_id on policy_creation_states, tool_call_logs, conversation_analytics

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # policy_creation_states
    op.drop_constraint('policy_creation_states_thread_id_fkey', 'policy_creation_states', type_='foreignkey')
    op.alter_column('policy_creation_states', 'thread_id', new_column_name='session_id',
                    existing_type=UUID(as_uuid=True), nullable=False)
    op.create_foreign_key(
        'policy_creation_states_session_id_fkey',
        'policy_creation_states', 'chat_sessions',
        ['session_id'], ['id']
    )

    # tool_call_logs
    op.drop_constraint('tool_call_logs_thread_id_fkey', 'tool_call_logs', type_='foreignkey')
    op.alter_column('tool_call_logs', 'thread_id', new_column_name='session_id',
                    existing_type=UUID(as_uuid=True), nullable=False)
    op.create_foreign_key(
        'tool_call_logs_session_id_fkey',
        'tool_call_logs', 'chat_sessions',
        ['session_id'], ['id']
    )

    # conversation_analytics — drop unique constraint first, rename, recreate
    op.drop_constraint('conversation_analytics_thread_id_fkey', 'conversation_analytics', type_='foreignkey')
    op.drop_constraint('conversation_analytics_thread_id_key', 'conversation_analytics', type_='unique')
    op.alter_column('conversation_analytics', 'thread_id', new_column_name='session_id',
                    existing_type=UUID(as_uuid=True), nullable=False)
    op.create_unique_constraint('conversation_analytics_session_id_key', 'conversation_analytics', ['session_id'])
    op.create_foreign_key(
        'conversation_analytics_session_id_fkey',
        'conversation_analytics', 'chat_sessions',
        ['session_id'], ['id']
    )


def downgrade() -> None:
    # conversation_analytics
    op.drop_constraint('conversation_analytics_session_id_fkey', 'conversation_analytics', type_='foreignkey')
    op.drop_constraint('conversation_analytics_session_id_key', 'conversation_analytics', type_='unique')
    op.alter_column('conversation_analytics', 'session_id', new_column_name='thread_id',
                    existing_type=UUID(as_uuid=True), nullable=False)
    op.create_unique_constraint('conversation_analytics_thread_id_key', 'conversation_analytics', ['thread_id'])
    op.create_foreign_key(
        'conversation_analytics_thread_id_fkey',
        'conversation_analytics', 'chat_sessions',
        ['thread_id'], ['id']
    )

    # tool_call_logs
    op.drop_constraint('tool_call_logs_session_id_fkey', 'tool_call_logs', type_='foreignkey')
    op.alter_column('tool_call_logs', 'session_id', new_column_name='thread_id',
                    existing_type=UUID(as_uuid=True), nullable=False)
    op.create_foreign_key(
        'tool_call_logs_thread_id_fkey',
        'tool_call_logs', 'chat_sessions',
        ['thread_id'], ['id']
    )

    # policy_creation_states
    op.drop_constraint('policy_creation_states_session_id_fkey', 'policy_creation_states', type_='foreignkey')
    op.alter_column('policy_creation_states', 'session_id', new_column_name='thread_id',
                    existing_type=UUID(as_uuid=True), nullable=False)
    op.create_foreign_key(
        'policy_creation_states_thread_id_fkey',
        'policy_creation_states', 'chat_sessions',
        ['thread_id'], ['id']
    )
