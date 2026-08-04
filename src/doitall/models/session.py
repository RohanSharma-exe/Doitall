"""Chat session data model."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from doitall.models.conversation import Conversation


class Session(BaseModel):
    """Session container grouping metadata, timestamps, and conversation history."""

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str = "New Chat"

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    conversation: Conversation = Field(default_factory=Conversation)

    metadata: dict[str, str] = Field(default_factory=dict)

