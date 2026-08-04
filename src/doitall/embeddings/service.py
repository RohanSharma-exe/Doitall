"""Abstract embedding service interface module."""

from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    """Abstract base class defining the contract for embedding generation services."""

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
