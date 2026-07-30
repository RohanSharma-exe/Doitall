from doitall.embeddings.manager import EmbeddingManager
from doitall.knowledge.chunker import DocumentChunker
from doitall.knowledge.document import Document
from doitall.knowledge.repository import KnowledgeRepository
from doitall.memory.vector_store import VectorStore
from doitall.serialization.chunk_serializer import ChunkSerializer


class VectorKnowledgeRepository(KnowledgeRepository):
    def __init__(
        self,
        chunker: DocumentChunker,
        embedding_manager: EmbeddingManager,
        vector_store: VectorStore,
    ) -> None:
        self.chunker = chunker
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    async def add(
        self,
        document: Document,
    ) -> int:
        chunks = self.chunker.chunk(document)

        for chunk in chunks:
            vector = await self.embedding_manager.embed(chunk.text)

            payload = ChunkSerializer.to_payload(chunk)

            self.vector_store.upsert(
                point_id=chunk.id,
                vector=vector,
                payload=payload,
            )

        return len(chunks)

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Document]:
        vector = await self.embedding_manager.embed(query)

        results = self.vector_store.search(
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

    def clear(self) -> None:
        self.vector_store.clear()

    def count(self) -> int:
        return self.vector_store.count()
