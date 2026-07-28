from doitall.memory.manager import MemoryManager
from doitall.runtime.context import RuntimeContext


class MemoryProvider:
    def __init__(
        self,
        memory: MemoryManager,
    ) -> None:
        self._memory = memory

    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        context.memories = self._memory.search(query)
