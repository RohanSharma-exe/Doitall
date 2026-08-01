import asyncio

from litellm import aembedding, embedding
from litellm.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
)

from doitall.core.exceptions import ConfigurationError, ProviderError
from doitall.embeddings.service import EmbeddingService


class LiteLLMEmbeddingService(EmbeddingService):
    def __init__(
        self,
        model: str,
    ) -> None:
        self.model = model

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            response = await aembedding(
                model=self.model,
                input=text,
            )
            return response.data[0]["embedding"]
        except AuthenticationError as e:
            raise ConfigurationError(
                f"Authentication failed for embedding model {self.model}: {e}"
            ) from e
        except RateLimitError as e:
            raise ProviderError(
                f"Rate limit exceeded for embedding model {self.model}: {e}"
            ) from e
        except ServiceUnavailableError as e:
            raise ProviderError(f"Embedding service unavailable: {e}") from e
        except Exception:
            # Fallback to synchronous embedding if async fails
            try:
                return await asyncio.to_thread(self._sync_embed, text)
            except Exception as fallback_error:
                raise ProviderError(
                    f"Failed to generate embedding: {fallback_error}"
                ) from fallback_error

    def _sync_embed(
        self,
        text: str,
    ) -> list[float]:
        try:
            response = embedding(
                model=self.model,
                input=text,
            )
            return response.data[0]["embedding"]
        except AuthenticationError as e:
            raise ConfigurationError(
                f"Authentication failed for embedding model {self.model}: {e}"
            ) from e
        except RateLimitError as e:
            raise ProviderError(
                f"Rate limit exceeded for embedding model {self.model}: {e}"
            ) from e
        except ServiceUnavailableError as e:
            raise ProviderError(f"Embedding service unavailable: {e}") from e
        except Exception as e:
            raise ProviderError(f"Failed to generate embedding: {e}") from e

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = await aembedding(
                model=self.model,
                input=texts,
            )
            return [item["embedding"] for item in response.data]
        except AuthenticationError as e:
            raise ConfigurationError(
                f"Authentication failed for embedding model {self.model}: {e}"
            ) from e
        except RateLimitError as e:
            raise ProviderError(
                f"Rate limit exceeded for embedding model {self.model}: {e}"
            ) from e
        except ServiceUnavailableError as e:
            raise ProviderError(f"Embedding service unavailable: {e}") from e
        except Exception:
            # Fallback to synchronous embedding if async fails
            try:
                return await asyncio.to_thread(self._sync_embed_batch, texts)
            except Exception as fallback_error:
                raise ProviderError(
                    f"Failed to generate embeddings: {fallback_error}"
                ) from fallback_error

    def _sync_embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        try:
            response = embedding(
                model=self.model,
                input=texts,
            )
            return [item["embedding"] for item in response.data]
        except AuthenticationError as e:
            raise ConfigurationError(
                f"Authentication failed for embedding model {self.model}: {e}"
            ) from e
        except RateLimitError as e:
            raise ProviderError(
                f"Rate limit exceeded for embedding model {self.model}: {e}"
            ) from e
        except ServiceUnavailableError as e:
            raise ProviderError(f"Embedding service unavailable: {e}") from e
        except Exception as e:
            raise ProviderError(f"Failed to generate embeddings: {e}") from e
