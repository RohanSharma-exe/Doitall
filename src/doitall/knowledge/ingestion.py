from doitall.knowledge.document import Document
from doitall.knowledge.repository import KnowledgeRepository


class KnowledgeIngestionService:
    def __init__(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        self.repository = repository

    def ingest(
        self,
        document: Document,
    ) -> None:
        self.repository.add(document)

    def ingest_many(
        self,
        documents: list[Document],
    ) -> None:
        for document in documents:
            self.repository.add(document)
