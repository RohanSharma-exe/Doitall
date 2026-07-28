from abc import ABC, abstractmethod

from doitall.knowledge.document import Document


class DocumentLoader(ABC):
    @abstractmethod
    def load(
        self,
        path: str,
    ) -> list[Document]:
        """Load one or more documents."""
