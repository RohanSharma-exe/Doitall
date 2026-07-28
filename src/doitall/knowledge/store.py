from abc import ABC, abstractmethod

from doitall.knowledge.document import Document


class KnowledgeStore(ABC):
    @abstractmethod
    def add(
        self,
        document: Document,
    ) -> None:
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Document]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
