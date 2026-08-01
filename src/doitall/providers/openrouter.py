import json
from typing import Any

from doitall.config.settings import settings
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall
from doitall.models.tool_definition import ToolDefinition
from doitall.providers.base import BaseProvider
from doitall.providers.client import LiteLLMClient


class OpenrouterProvider(BaseProvider):
    def __init__(self) -> None:
        super().__init__("openrouter")
        self.client = LiteLLMClient()

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> ProviderResponse:
        tools = kwargs.pop("tools", [])

        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        response = await self.client.chat(
            model=settings.OPENROUTER_MODEL,
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
        )

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
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

    def _convert_tools(
        self,
        tools: list[ToolDefinition],
    ) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]

    def _parse_tool_calls(
        self,
        message: Any,
    ) -> list[ToolCall]:
        tool_calls: list[ToolCall] = []

        for call in getattr(message, "tool_calls", []) or []:
            tool_calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=json.loads(call.function.arguments),
                )
            )

        return tool_calls
