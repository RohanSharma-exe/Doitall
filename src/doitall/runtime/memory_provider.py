"""Memory search context provider module."""

from doitall.memory.manager import MemoryManager
from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider


class MemoryProvider(ContextProvider):
    """Adds relevant memories to the runtime context based on semantic query search."""

    def __init__(
        self,
        manager: MemoryManager,
        limit: int = 5,
    ) -> None:
        """Initialize memory provider with MemoryManager dependency and retrieval limit."""
        self._manager = manager
        self._limit = limit

    async def populate(
        self,
        context: RuntimeContext,
    ) -> None:
        """Search memory store using query and append matching memories to context."""
        # Use the structured query field first; fall back to last message content.
        query = context.query or (
            context.messages[-1].content if context.messages else ""
        )

        if not query:
            return

        context.memories.extend(
            await self._manager.search(
                query=query,
                limit=self._limit,
            )
        )

