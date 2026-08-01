from doitall.knowledge.repository import KnowledgeRepository
from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider


class KnowledgeProvider(ContextProvider):
    """Adds semantically relevant knowledge chunks to the runtime context."""

    def __init__(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        self._repository = repository

    async def populate(
        self,
        context: RuntimeContext,
    ) -> None:
        if not context.query:
            return

        context.knowledge.extend(await self._repository.search(context.query))
