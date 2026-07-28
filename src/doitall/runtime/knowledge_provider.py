from doitall.knowledge.repository import KnowledgeRepository
from doitall.runtime.context import RuntimeContext


class KnowledgeProvider:
    def __init__(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        self._repository = repository

    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        context.knowledge = self._repository.search(query)
