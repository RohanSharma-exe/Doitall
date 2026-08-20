import json
from collections.abc import AsyncIterator
from typing import Any

from loguru import logger

from doitall.models.message import (
    AssistantMessage,
    Message,
    ToolMessage,
)
from doitall.models.provider_response import ProviderResponse
from doitall.providers.exceptions import is_retryable_provider_error
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

    def _payload(self, messages: list[Message]) -> list[dict[str, Any]]:
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

        return payload

    @staticmethod
    def _should_retry_without_tools(exc: Exception, has_tools: bool) -> bool:
        if not has_tools:
            return False

        message = str(exc).lower()
        return any(
            marker in message
            for marker in (
                "tool_use_failed",
                "failed to call a function",
                "tool calling",
                "tool call",
                "function call",
            )
        )

    async def stream(
        self,
        context: RuntimeContext,
    ) -> AsyncIterator[Any]:
        messages = self.prepare(context)
        payload = self._payload(messages)
        errors: list[Exception] = []

        for candidate in self._provider_manager.fallback_candidates(context.provider):
            emitted_output = False
            try:
                async for chunk in candidate.provider.stream(
                    payload,
                    tools=context.tools,
                    model=context.model,
                ):
                    emitted_output = True
                    yield chunk

                return

            except Exception as exc:
                if emitted_output:
                    raise

                if self._should_retry_without_tools(exc, bool(context.tools)):
                    logger.warning(
                        "Provider '{}' rejected tool calling while streaming. Retrying without tools.",
                        candidate.provider.name,
                    )

                    try:
                        async for chunk in candidate.provider.stream(
                            payload,
                            tools=[],
                            model=context.model,
                        ):
                            emitted_output = True
                            yield chunk

                        return

                    except Exception as retry_exc:
                        if emitted_output:
                            raise

                        exc = retry_exc
                        logger.warning(
                            "Retry without tools also failed for '{}': {}",
                            candidate.provider.name,
                            retry_exc,
                        )

                errors.append(exc)
                if not is_retryable_provider_error(exc):
                    raise exc

                logger.warning(
                    "Provider '{}' failed with a retryable error: {}",
                    candidate.provider.name,
                    exc,
                )

        if errors:
            raise errors[-1]
        raise RuntimeError("No provider configured.")

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

        payload = self._payload(messages)
        errors: list[Exception] = []

        for candidate in self._provider_manager.fallback_candidates(context.provider):
            try:
                response = await candidate.provider.chat(
                    payload,
                    tools=context.tools,
                    model=context.model,
                )

                if isinstance(response, ProviderResponse) and response.model is None:
                    response.model = context.model

                return response

            except Exception as exc:
                if self._should_retry_without_tools(exc, bool(context.tools)):
                    logger.warning(
                        "Provider '{}' rejected tool calling. Retrying without tools.",
                        candidate.provider.name,
                    )

                    try:
                        response = await candidate.provider.chat(
                            payload,
                            tools=[],
                            model=context.model,
                        )

                        if (
                            isinstance(response, ProviderResponse)
                            and response.model is None
                        ):
                            response.model = context.model

                        return response

                    except Exception as retry_exc:
                        exc = retry_exc
                        logger.warning(
                            "Retry without tools also failed for '{}': {}",
                            candidate.provider.name,
                            retry_exc,
                        )

                errors.append(exc)
                if not is_retryable_provider_error(exc):
                    raise exc

                logger.warning(
                    "Provider '{}' failed with a retryable error: {}",
                    candidate.provider.name,
                    exc,
                )

        if errors:
            raise errors[-1]
        raise RuntimeError("No provider configured.")
