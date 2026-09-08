"""Generic LiteLLM provider — replaces all per-provider subclasses.

One instance is registered per configured provider, parameterised by name and
the default model string drawn from settings.  An optional ``health_check_fn``
callable lets providers override the default ping-based check (e.g. Ollama,
which hits a local HTTP endpoint instead).
"""

from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

from doitall.models.provider_response import ProviderResponse
from doitall.providers.base import BaseProvider
from doitall.providers.client import LiteLLMClient


class LiteLLMProvider(BaseProvider):
    """Concrete LLM provider backed by LiteLLM, parameterised by name and default model."""

    def __init__(
        self,
        name: str,
        default_model: str,
        *,
        health_check_fn: Callable[[], Coroutine[Any, Any, bool]] | None = None,
    ) -> None:
        """Initialise provider.

        Args:
            name: Human-readable provider identifier (e.g. ``"openai"``).
            default_model: LiteLLM model string used when the caller does not
                supply an explicit model (e.g. ``"gpt-4o"``).
            health_check_fn: Optional async callable returning ``True`` when the
                provider is reachable.  Defaults to a minimal 1-token chat ping.
        """
        super().__init__(name)
        self._default_model = default_model
        self._health_check_fn = health_check_fn
        self.client = LiteLLMClient()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResponse:
        """Execute a chat completion request."""
        tools = kwargs.pop("tools", [])
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        response = await self.client.chat(
            model=kwargs.pop("model", None) or self._default_model,
            messages=messages,
            **kwargs,
        )
        return self._to_provider_response(response)

    async def stream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        """Stream response chunks from the provider."""
        tools = kwargs.pop("tools", [])
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        async for chunk in self.client.stream(
            model=kwargs.pop("model", None) or self._default_model,
            messages=messages,
            **kwargs,
        ):
            yield chunk

    async def health_check(self) -> bool:
        """Return True when the provider is reachable."""
        if self._health_check_fn is not None:
            return await self._health_check_fn()

        try:
            await self.client.chat(
                model=self._default_model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_provider_response(self, response: Any) -> ProviderResponse:
        message = response.choices[0].message
        return ProviderResponse(
            content=message.content or "",
            tool_calls=self._parse_tool_calls(message),
            finish_reason=response.choices[0].finish_reason,
            model=response.model,
            usage_tokens=self._parse_usage(response),
        )

    def _parse_usage(self, response: Any) -> dict[str, int]:
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
