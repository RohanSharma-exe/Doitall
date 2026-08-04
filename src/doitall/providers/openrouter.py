"""OpenRouter provider integration module."""

from typing import Any

from doitall.config.settings import settings
from doitall.models.provider_response import ProviderResponse
from doitall.providers.base import BaseProvider
from doitall.providers.client import LiteLLMClient


class OpenrouterProvider(BaseProvider):
    """Provider implementation for OpenRouter model API gateway via LiteLLM."""

    def __init__(self) -> None:
        super().__init__("openrouter")
        self.client = LiteLLMClient()

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResponse:
        """Execute OpenRouter chat completion with optional tool calls."""
        tools = kwargs.pop("tools", [])

        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        response = await self.client.chat(
            model=kwargs.pop("model", None) or settings.OPENROUTER_MODEL,
            messages=messages,
            **kwargs,
        )

        return self._to_provider_response(response)

    def _to_provider_response(
        self,
        response: Any,
    ) -> ProviderResponse:
        """Convert a LiteLLM response into Doitall's normalized response."""

        message = response.choices[0].message

        return ProviderResponse(
            content=message.content or "",
            tool_calls=self._parse_tool_calls(message),
            finish_reason=response.choices[0].finish_reason,
            model=response.model,
            usage_tokens=self._parse_usage(response),
        )

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ):
        """Stream response chunks from OpenRouter models."""
        tools = kwargs.pop("tools", [])
        if tools:
            kwargs["tools"] = self._convert_tools(tools)
        async for chunk in self.client.stream(
            model=kwargs.pop("model", None) or settings.OPENROUTER_MODEL,
            messages=messages,
            **kwargs,
        ):
            yield chunk

    def _parse_usage(self, response: Any) -> dict[str, int]:
        """Extract prompt, completion, and total token usage metrics."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return {}
        result: dict[str, int] = {}
        for source, target in (
            ("prompt_tokens", "prompt"),
            ("completion_tokens", "completion"),
            ("total_tokens", "total"),
        ):
            value = getattr(usage, source, None)
            if value is not None:
                result[target] = int(value)
        return result

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        """Generate text embeddings (not supported by OpenRouter)."""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """Validate connectivity by making a minimal 1-token completion call."""
        try:
            await self.client.chat(
                model=settings.OPENROUTER_MODEL,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False

