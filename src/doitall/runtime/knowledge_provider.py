from doitall.knowledge.repository import KnowledgeRepository
from doitall.runtime.context import RuntimeContext


class KnowledgeProvider:
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

        context.knowledge = self._repository.search(context.query)
