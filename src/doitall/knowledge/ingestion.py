from doitall.core.exceptions import ProviderError, ValidationError
from doitall.knowledge.document import Document
from doitall.knowledge.repository import KnowledgeRepository


class KnowledgeIngestionService:
    def __init__(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        self.repository = repository

    async def ingest(
        self,
        document: Document,
    ) -> None:
        if not document or not document.content or not document.content.strip():
            raise ValidationError("Document content cannot be empty")

        await self.repository.add(document)

    async def ingest_many(
        self,
        documents: list[Document],
    ) -> None:
        if not documents:
            return

        failed_documents = []

        for document in documents:
            try:
                await self.ingest(document)
            except Exception as e:
                failed_documents.append((document.id if document else "unknown", str(e)))

        if failed_documents:
            error_msg = f"Failed to ingest {len(failed_documents)} out of {len(documents)} documents. "
            error_msg += f"Failed document IDs: {[doc_id for doc_id, _ in failed_documents]}"
            raise ProviderError(error_msg)
