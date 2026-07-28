from doitall.embeddings.litellm_service import LiteLLMEmbeddingService
from doitall.embeddings.service import EmbeddingService


class EmbeddingManager:
    def __init__(
        self,
        service: EmbeddingService,
    ) -> None:
        self.service = service

    def embed(
        self,
        text: str,
    ) -> list[float]:
        return self.service.embed(text)

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return self.service.embed_batch(texts)

    @classmethod
    def from_model(
        cls,
        model: str,
    ) -> EmbeddingManager:
        return cls(
            LiteLLMEmbeddingService(model=model),
        )
