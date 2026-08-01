"""ConversationService — manages a single session's message history.

Two modes:
- **In-memory** (default): messages live in a Python list. Used by tests and
  one-shot calls that don't need persistence.
- **DB-backed**: pass ``session_id`` and ``repository`` to write every message
  through to the database immediately, and hydrate from DB on first access.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from doitall.config.settings import settings
from doitall.models.conversation import Conversation
from doitall.models.message import (
    AssistantMessage,
    Message,
    MessageRole,
    SystemMessage,
    ToolMessage,
    UserMessage,
)

if TYPE_CHECKING:
    from doitall.database.session_repository import SessionRepository


def _record_to_message(record) -> Message:  # type: ignore[no-untyped-def]
    """Convert a ``MessageRecord`` ORM row to a domain ``Message`` object."""
    role = record.role
    if role == MessageRole.USER:
        return UserMessage(content=record.content)
    if role == MessageRole.ASSISTANT:
        from doitall.models.tool_call import ToolCall

        tool_calls = [
            ToolCall(**tc) for tc in record.get_tool_calls()
        ]
        return AssistantMessage(content=record.content, tool_calls=tool_calls)
    if role == MessageRole.SYSTEM:
        return SystemMessage(content=record.content)
    if role == MessageRole.TOOL:
        return ToolMessage(
            content=record.content,
            tool_call_id=record.tool_call_id or "",
            name=record.name or "",
        )
    # Fallback: return as generic Message
    return Message(role=role, content=record.content)


class ConversationService:
    def __init__(
        self,
        conversation: Conversation | None = None,
        session_id: str | None = None,
        repository: SessionRepository | None = None,
    ) -> None:
        self._conversation = conversation or Conversation()
        self._session_id = session_id
        self._repository = repository
        self._hydrated = False  # lazy-load flag for DB mode

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_hydrated(self) -> None:
        """Load messages from DB into the in-memory conversation (once)."""
        if self._hydrated or self._repository is None or self._session_id is None:
            self._hydrated = True
            return
        records = self._repository.get_messages(self._session_id)
        for record in records:
            msg = _record_to_message(record)
            self._conversation.messages.append(msg)
        self._hydrated = True

    def _persist(self, message: Message) -> None:
        """Write a single message to the DB (no-op in in-memory mode)."""
        if self._repository is None or self._session_id is None:
            return

        role = message.role
        tool_calls: list[dict] | None = None
        tool_call_id: str | None = None
        name: str | None = None

        if isinstance(message, AssistantMessage) and message.tool_calls:
            tool_calls = [tc.model_dump() for tc in message.tool_calls]
        if isinstance(message, ToolMessage):
            tool_call_id = message.tool_call_id
            name = message.name

        self._repository.append_message(
            session_id=self._session_id,
            role=role,
            content=message.content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            name=name,
        )

    # ------------------------------------------------------------------
    # Public API (unchanged interface for existing callers)
    # ------------------------------------------------------------------

    @property
    def conversation(self) -> Conversation:
        self._ensure_hydrated()
        return self._conversation

    def add_message(self, message: Message) -> None:
        self._ensure_hydrated()
        self._conversation.messages.append(message)
        self._persist(message)

    def messages(self) -> list[Message]:
        self._ensure_hydrated()
        return list(self._conversation.messages)

    def context_messages(self, max_messages: int | None = None) -> list[Message]:
        """Return a bounded sliding window for provider context."""
        self._ensure_hydrated()
        limit = settings.MAX_HISTORY_MESSAGES if max_messages is None else max_messages
        if limit <= 0:
            return []
        return list(self._conversation.messages[-limit:])

    def clear(self) -> None:
        self._conversation.messages.clear()
        self._hydrated = False
        if self._repository and self._session_id:
            self._repository.clear_messages(self._session_id)

    def last_message(self) -> Message | None:
        self._ensure_hydrated()
        if not self._conversation.messages:
            return None
        return self._conversation.messages[-1]
