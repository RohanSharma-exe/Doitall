from doitall.embeddings.litellm_service import LiteLLMEmbeddingService
from doitall.embeddings.service import EmbeddingService


class EmbeddingManager:
    def __init__(
        self,
        service: EmbeddingService,
    ) -> None:
        self.service = service

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        return await self.service.embed(text)

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return await self.service.embed_batch(texts)

    @classmethod
    def from_model(
        cls,
        model: str,
    ) -> EmbeddingManager:
        return cls(
            LiteLLMEmbeddingService(model=model),
        )
