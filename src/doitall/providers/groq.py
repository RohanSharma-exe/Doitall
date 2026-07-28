from typing import Any

from doitall.config.settings import settings
from doitall.providers.base import BaseProvider
from doitall.providers.client import LiteLLMClient


class GroqProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("groq")
        self.client = LiteLLMClient()

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        response = await self.client.chat(
            model=settings.GROQ_MODEL,
            messages=messages,
            **kwargs,
        )

        return response.choices[0].message.content

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True
