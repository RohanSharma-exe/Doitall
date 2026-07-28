from abc import ABC, abstractmethod
from typing import Any

from doitall.models.provider_response import ProviderResponse


class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResponse:
        """Send a chat completion request."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is healthy."""

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ):
        raise NotImplementedError(f"{self.name} does not support streaming.")

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        raise NotImplementedError(f"{self.name} does not support embeddings.")

    async def image_understanding(
        self,
        image: Any,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError(f"{self.name} does not support image understanding.")

    async def image_generation(
        self,
        prompt: str,
        **kwargs: Any,
    ):
        raise NotImplementedError(f"{self.name} does not support image generation.")

    async def speech_to_text(
        self,
        audio: Any,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError(f"{self.name} does not support speech-to-text.")

    async def text_to_speech(
        self,
        text: str,
        **kwargs: Any,
    ):
        raise NotImplementedError(f"{self.name} does not support text-to-speech.")

    async def tool_call(
        self,
        messages: list[dict],
        tools: list[dict],
        **kwargs: Any,
    ):
        raise NotImplementedError(f"{self.name} does not support tool calling.")

    def capabilities(self) -> dict[str, bool]:
        return {
            "chat": True,
            "stream": False,
            "embedding": False,
            "image_understanding": False,
            "image_generation": False,
            "speech_to_text": False,
            "text_to_speech": False,
            "tool_call": False,
        }

    async def available_models(self) -> list[str]:
        return []
