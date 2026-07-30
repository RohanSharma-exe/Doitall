import json
from typing import Any

from doitall.models.message import (
    AssistantMessage,
    Message,
    ToolMessage,
)
from doitall.models.provider_response import ProviderResponse
from doitall.providers.manager import ProviderManager
from doitall.runtime.context import RuntimeContext
from doitall.runtime.prompt_builder import PromptBuilder


class RuntimeExecutor:
    """Executes a single request against the configured provider.

    The RuntimeExecutor is responsible for preparing messages and sending
    them to the LLM provider for processing.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        provider_manager: ProviderManager,
    ) -> None:
        """Initialize the runtime executor.

        Args:
            prompt_builder: Builder for constructing prompts from context.
            provider_manager: Manager for accessing LLM providers.
        """
        self._prompt_builder = prompt_builder
        self._provider_manager = provider_manager

    def prepare(
        self,
        context: RuntimeContext,
    ) -> list[Message]:
        """Prepare messages for the LLM provider.

        Args:
            context: The runtime context containing conversation state.

        Returns:
            List of messages formatted for the LLM provider.
        """
        return self._prompt_builder.build(context)

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        """Execute the request against the configured provider.

        Args:
            context: The runtime context containing conversation state and tools.

        Returns:
            The provider's response with content and tool calls.
        """
        messages = self.prepare(context)

        provider = (
            self._provider_manager.get(context.provider)
            if context.provider
            else self._provider_manager.default()
        )

        payload: list[dict[str, Any]] = []

        for message in messages:
            item: dict[str, Any] = {
                "role": message.role.value,
                "content": message.content,
            }

            if isinstance(message, AssistantMessage) and message.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(call.arguments),
                        },
                    }
                    for call in message.tool_calls
                ]

            if isinstance(message, ToolMessage):
                item["tool_call_id"] = message.tool_call_id
                item["name"] = message.name

            payload.append(item)

        return await provider.chat(payload, tools=context.tools)
