"""add composite message history index

Revision ID: 0003_message_history_index
Revises: 0002_add_execution_metadata
Create Date: 2026-08-14
"""

from alembic import op

revision = "0003_message_history_index"
down_revision = "0002_add_execution_metadata"
branch_labels = None
depends_on = None

_INDEX_NAME = "ix_messages_session_created_at"


def upgrade() -> None:
    op.create_index(
        _INDEX_NAME,
        "messages",
        ["session_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(_INDEX_NAME, table_name="messages")
