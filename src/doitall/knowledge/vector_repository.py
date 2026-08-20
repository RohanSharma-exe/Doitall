"""Vector store implementation of KnowledgeRepository."""

from typing import Any

from doitall.core.exceptions import ProviderError
from doitall.embeddings.manager import EmbeddingManager
from doitall.knowledge.chunker import DocumentChunker
from doitall.knowledge.document import Document
from doitall.knowledge.repository import KnowledgeRepository
from doitall.memory.vector_store import VectorStore
from doitall.serialization.chunk_serializer import ChunkSerializer


class VectorKnowledgeRepository(KnowledgeRepository):
    """Vector database backed knowledge repository for semantic RAG document search."""

    def __init__(
        self,
        chunker: DocumentChunker,
        embedding_manager: EmbeddingManager,
        vector_store: VectorStore,
    ) -> None:
        """Initialize repository with chunker, embedding manager, and vector store dependencies."""
        self.chunker = chunker
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    async def add(
        self,
        document: Document,
    ) -> int:
        """Chunk document, embed text, and upsert points into vector store."""
        chunks = self.chunker.chunk(document)
        if not chunks:
            return 0

        vectors = await self.embedding_manager.embed_batch(
            [chunk.text for chunk in chunks]
        )
        if len(vectors) != len(chunks):
            raise ProviderError(
                "Embedding provider returned a different number of vectors than chunks"
            )

        await self.vector_store.upsert_many(
            [
                (chunk.id, vector, ChunkSerializer.to_payload(chunk))
                for chunk, vector in zip(chunks, vectors, strict=True)
            ]
        )

        return len(chunks)

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Document]:
        """Embed search query and perform vector similarity search."""
        vector = await self.embedding_manager.embed(query)

        results = await self.vector_store.search(
            vector=vector,
            limit=limit,
        )

        documents: list[Document] = []

        for result in results:
            payload = result["payload"]

            document_id = payload.get("document_id")
            text = payload.get("text")

            # Skip any stale points that don't match the chunk payload schema
            if not document_id or not text:
                continue

            documents.append(
                Document(
                    id=document_id,
                    content=text,
                    metadata=payload.get("metadata", {}),
                )
            )

        return documents

    async def delete(self, document_id: str) -> int:
        """Delete all chunks whose payload.document_id matches *document_id*.

        Returns the number of chunk points removed.  Scrolls the entire
        collection to find matching points because Qdrant filter-delete on
        payload fields requires a filter query rather than a point-ID list.
        """
        all_points = await self.vector_store.scroll_all()
        matching_ids = [
            p["id"]
            for p in all_points
            if (p.get("payload") or {}).get("document_id") == document_id
        ]
        for point_id in matching_ids:
            await self.vector_store.delete(point_id)
        return len(matching_ids)

    async def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return a paged summary list of indexed documents.

        Each entry has: document_id, title (from metadata), chunk_count, metadata.
        The list is ordered by insertion order (as returned by Qdrant scroll).
        """
        all_points = await self.vector_store.scroll_all()

        # Group by document_id, accumulating chunk count and metadata.
        seen: dict[str, dict[str, Any]] = {}
        order: list[str] = []  # Preserve first-seen order
        for point in all_points:
            payload = point.get("payload") or {}
            doc_id = payload.get("document_id")
            if not doc_id:
                continue
            if doc_id not in seen:
                seen[doc_id] = {
                    "document_id": doc_id,
                    "title": payload.get("metadata", {}).get("title"),
                    "chunk_count": 0,
                    "metadata": payload.get("metadata", {}),
                }
                order.append(doc_id)
            seen[doc_id]["chunk_count"] += 1

        paged = order[offset : offset + limit]
        return [seen[doc_id] for doc_id in paged]

    async def clear(self) -> None:
        """Clear all indexed document chunks from vector store."""
        await self.vector_store.clear()

    async def count(self) -> int:
        """Return total count of indexed document chunks in vector store."""
        return await self.vector_store.count()
