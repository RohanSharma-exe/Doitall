"""Fluent builder pattern for constructing RuntimeContext instances."""

from doitall.knowledge.document import Document
from doitall.models.memory import Memory
from doitall.models.message import Message
from doitall.runtime.context import RuntimeContext


class ContextBuilder:
    """Fluent builder for creating and populating RuntimeContext objects."""

    def __init__(self) -> None:
        """Initialize empty context builder."""
        self._context = RuntimeContext()

    def add_messages(
        self,
        messages: list[Message],
    ) -> ContextBuilder:
        """Add list of conversation messages to context."""
        self._context.messages.extend(messages)
        return self

    def add_memories(
        self,
        memories: list[Memory],
    ) -> ContextBuilder:
        """Add list of memory items to context."""
        self._context.memories.extend(memories)
        return self

    def add_knowledge(
        self,
        documents: list[Document],
    ) -> ContextBuilder:
        """Add list of knowledge documents to context."""
        self._context.knowledge.extend(documents)
        return self

    def build(self) -> RuntimeContext:
        """Return the built RuntimeContext instance."""
        return self._context
