"""Knowledge document ingestion service module."""

from doitall.core.exceptions import ProviderError, ValidationError
from doitall.knowledge.document import Document
from doitall.knowledge.repository import KnowledgeRepository


class IngestionResult:
    """Ingestion result detailing document ID, chunk count, and status."""

    def __init__(
        self,
        *,
        document_id: str,
        chunk_count: int,
        status: str = "ingested",
    ) -> None:
        self.document_id = document_id
        self.chunk_count = chunk_count
        self.status = status


class KnowledgeIngestionService:
    """Service handling validation, chunking, and vector storage of ingested documents."""

    def __init__(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        """Initialize ingestion service with target KnowledgeRepository dependency."""
        self.repository = repository

    async def ingest(
        self,
        document: Document,
    ) -> IngestionResult:
        """Validate, chunk, embed, and index a single Document object."""
        if not document or not document.content or not document.content.strip():
            raise ValidationError("Document content cannot be empty")

        chunk_count = await self.repository.add(document)

        return IngestionResult(
            document_id=document.id,
            chunk_count=chunk_count,
        )

    async def ingest_many(
        self,
        documents: list[Document],
    ) -> list[IngestionResult]:
        """Ingest multiple documents in sequence, accumulating and reporting batch errors."""
        if not documents:
            return []

        failed_documents = []
        results: list[IngestionResult] = []

        for document in documents:
            try:
                results.append(await self.ingest(document))
            except Exception as e:
                failed_documents.append(
                    (document.id if document else "unknown", str(e))
                )

        if failed_documents:
            error_msg = f"Failed to ingest {len(failed_documents)} out of {len(documents)} documents. "
            error_msg += (
                f"Failed document IDs: {[doc_id for doc_id, _ in failed_documents]}"
            )
            raise ProviderError(error_msg)

        return results
