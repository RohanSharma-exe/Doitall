from litellm import embedding

from doitall.embeddings.service import EmbeddingService


class LiteLLMEmbeddingService(EmbeddingService):
    def __init__(
        self,
        model: str,
    ) -> None:
        self.model = model

    def embed(
        self,
        text: str,
    ) -> list[float]:
        response = embedding(
            model=self.model,
            input=text,
        )

        return response.data[0]["embedding"]

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        response = embedding(
            model=self.model,
            input=texts,
        )

        return [item["embedding"] for item in response.data]
