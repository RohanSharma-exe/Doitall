import json

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
    """Executes a single request against the configured provider."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        provider_manager: ProviderManager,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._provider_manager = provider_manager

    def prepare(
        self,
        context: RuntimeContext,
    ) -> list[Message]:
        return self._prompt_builder.build(context)

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        messages = self.prepare(context)

        provider = self._provider_manager.default()

        payload: list[dict] = []

        for message in messages:
            item = {
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
