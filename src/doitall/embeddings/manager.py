"""Embedding manager wrapper module."""

from doitall.embeddings.litellm_service import LiteLLMEmbeddingService
from doitall.embeddings.service import EmbeddingService


class EmbeddingManager:
    """Delegates embedding generation calls to configured EmbeddingService instance."""

    def __init__(
        self,
        service: EmbeddingService,
    ) -> None:
        """Initialize EmbeddingManager with an EmbeddingService instance."""
        self.service = service

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate embedding vector for single input text string."""
        return await self.service.embed(text)

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embedding vectors for batch of input text strings."""
        return await self.service.embed_batch(texts)

    @classmethod
    def from_model(
        cls,
        model: str,
    ) -> EmbeddingManager:
        """Construct EmbeddingManager using LiteLLMEmbeddingService for specified model."""
        return cls(
            LiteLLMEmbeddingService(model=model),
        )
