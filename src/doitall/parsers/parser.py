from abc import ABC, abstractmethod

from doitall.knowledge.document import Document


class DocumentParser(ABC):
    @abstractmethod
    def parse(
        self,
        path: str,
    ) -> list[Document]:
        """Parse a file into one or more documents."""
