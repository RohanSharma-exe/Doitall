"""Abstract base provider interface module.

Defines the contract for LLM provider implementations including chat completion,
streaming, embeddings, tool conversion, and response parsing.
"""

import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Mapping
from typing import Any

from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall
from doitall.models.tool_definition import ToolDefinition
from doitall.providers.exceptions import ProviderResponseError


class BaseProvider(ABC):
    """Abstract base class for all LLM provider integrations."""

    def __init__(self, name: str):
        """Initialize provider with unique string identifier."""
        self.name = name

    @abstractmethod
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
    ) -> AsyncIterator[Any]:
        """Stream text generation chunks from the provider."""
        _ = (messages, kwargs)
        raise NotImplementedError(f"{self.name} does not support streaming.")
        if False:
            yield

    async def embedding(
        self,
        text: str,
        **kwargs: Any,
    ) -> list[float]:
        """Generate vector embedding representation of input text."""
        raise NotImplementedError(f"{self.name} does not support embeddings.")

    async def image_understanding(
        self,
        image: Any,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Process image input with textual prompt for vision analysis."""
        raise NotImplementedError(f"{self.name} does not support image understanding.")

    async def image_generation(
        self,
        prompt: str,
        **kwargs: Any,
    ):
        """Generate images based on textual prompt."""
        raise NotImplementedError(f"{self.name} does not support image generation.")

    async def speech_to_text(
        self,
        audio: Any,
        **kwargs: Any,
    ) -> str:
        """Transcribe audio input to text."""
        raise NotImplementedError(f"{self.name} does not support speech-to-text.")

    async def text_to_speech(
        self,
        text: str,
        **kwargs: Any,
    ):
        """Synthesize text input into audio speech."""
        raise NotImplementedError(f"{self.name} does not support text-to-speech.")

    async def tool_call(
        self,
        messages: list[dict],
        tools: list[dict],
        **kwargs: Any,
    ):
        """Execute chat completion with tool calling capabilities."""
        raise NotImplementedError(f"{self.name} does not support tool calling.")

    def capabilities(self) -> dict[str, bool]:
        """Return dictionary of supported feature capabilities."""
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
        """Return list of supported model identifiers."""
        return []

    def _convert_tools(
        self,
        tools: list[ToolDefinition],
    ) -> list[dict[str, Any]]:
        """Convert domain tool definitions to OpenAI-compatible function schema dicts."""
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
        """Extract and parse tool call objects from provider response message."""
        tool_calls: list[ToolCall] = []

        for call in getattr(message, "tool_calls", []) or []:
            raw_arguments = getattr(call.function, "arguments", {})
            tool_calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=self._parse_tool_arguments(raw_arguments),
                )
            )

        return tool_calls

    def _parse_tool_arguments(self, arguments: Any) -> dict[str, Any]:
        """Parse raw tool call argument string or object into dictionary."""
        if arguments in (None, ""):
            return {}

        if isinstance(arguments, str):
            try:
                decoded = json.loads(arguments)
            except json.JSONDecodeError as exc:
                raise ProviderResponseError(
                    "Tool call arguments are not valid JSON."
                ) from exc
        else:
            decoded = arguments

        if not isinstance(decoded, Mapping):
            raise ProviderResponseError("Tool call arguments must be a JSON object.")

        return dict(decoded)
