from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding for a single text."""

    @abstractmethod
    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
