from typing import Any

from doitall.config.settings import settings
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall
from doitall.providers.base import BaseProvider
from doitall.providers.client import LiteLLMClient


class GeminiProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("gemini")
        self.client = LiteLLMClient()

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResponse:
        response = await self.client.chat(
            model=settings.GEMINI_MODEL,
            messages=messages,
            **kwargs,
        )

        message = response.choices[0].message

        tool_calls: list[ToolCall] = []

        return ProviderResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason,
            model=response.model,
        )

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True
