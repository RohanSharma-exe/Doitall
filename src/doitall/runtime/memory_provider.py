from doitall.memory.manager import MemoryManager
from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider


class MemoryProvider(ContextProvider):
    """Adds relevant memories to the runtime context."""

    def __init__(
        self,
        manager: MemoryManager,
        limit: int = 5,
    ) -> None:
        self._manager = manager
        self._limit = limit

    async def populate(
        self,
        context: RuntimeContext,
    ) -> None:
        # Use the structured query field first; fall back to last message content.
        query = context.query or (
            context.messages[-1].content if context.messages else ""
        )

        if not query:
            return

        context.memories.extend(
            self._manager.search(
                query=query,
                limit=self._limit,
            )
        )
