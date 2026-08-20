"""add tool execution metadata to messages

Revision ID: 0002_add_execution_metadata
Revises: 0001_initial_sessions
Create Date: 2026-08-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_add_execution_metadata"
down_revision = "0001_initial_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("execution_metadata_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("messages", "execution_metadata_json")
