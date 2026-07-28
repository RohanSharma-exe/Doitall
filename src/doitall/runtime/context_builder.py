from doitall.knowledge.document import Document
from doitall.models.memory import Memory
from doitall.models.message import Message
from doitall.runtime.context import RuntimeContext


class ContextBuilder:
    def __init__(self) -> None:
        self._context = RuntimeContext()

    def add_messages(
        self,
        messages: list[Message],
    ) -> ContextBuilder:
        self._context.messages.extend(messages)
        return self

    def add_memories(
        self,
        memories: list[Memory],
    ) -> ContextBuilder:
        self._context.memories.extend(memories)
        return self

    def add_knowledge(
        self,
        documents: list[Document],
    ) -> ContextBuilder:
        self._context.knowledge.extend(documents)
        return self

    def build(self) -> RuntimeContext:
        return self._context
