"""Persisted database models for sessions and conversation messages."""

import json
from datetime import UTC, datetime

from sqlmodel import Column, Field, Relationship, SQLModel, Text


def _now() -> datetime:
    return datetime.now(UTC)


class SessionRecord(SQLModel, table=True):
    """One row per chat session. Keyed by the client-supplied session_id."""

    __tablename__ = "sessions"

    session_id: str = Field(primary_key=True)
    agent_name: str = Field(default="Doitall")
    system_prompt: str = Field(default="You are a helpful AI assistant.")
    provider: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=_now)
    last_accessed_at: datetime = Field(default_factory=_now)

    messages: list[MessageRecord] = Relationship(back_populates="session")


class MessageRecord(SQLModel, table=True):
    """One row per message turn within a session."""

    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.session_id", index=True)
    role: str  # user | assistant | system | tool
    content: str = Field(default="", sa_column=Column(Text))

    # AssistantMessage may carry tool_calls (stored as a JSON string)
    tool_calls_json: str | None = Field(default=None, sa_column=Column(Text))

    # ToolMessage extra fields
    tool_call_id: str | None = Field(default=None)
    name: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=_now)

    session: SessionRecord | None = Relationship(back_populates="messages")

    # ------------------------------------------------------------------
    # Helpers for serialising / deserialising tool_calls list
    # ------------------------------------------------------------------

    def set_tool_calls(self, tool_calls: list[dict]) -> None:
        self.tool_calls_json = json.dumps(tool_calls) if tool_calls else None

    def get_tool_calls(self) -> list[dict]:
        if not self.tool_calls_json:
            return []
        return json.loads(self.tool_calls_json)
