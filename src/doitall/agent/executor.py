from collections.abc import AsyncIterator
from typing import Any

from loguru import logger

from doitall.config.settings import settings
from doitall.models.message import AssistantMessage
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall
from doitall.runtime.context import RuntimeContext
from doitall.runtime.executor import RuntimeExecutor
from doitall.runtime.tool_message_builder import ToolMessageBuilder
from doitall.services.tool_calling_engine import ToolCallingEngine


class AgentExecutor:
    """Coordinates runtime execution and iterative tool calling until completion."""

    def __init__(
        self,
        runtime: RuntimeExecutor,
        tool_engine: ToolCallingEngine,
        tool_message_builder: ToolMessageBuilder,
    ) -> None:
        """Initialize AgentExecutor with runtime, tool engine, and message builder dependencies."""
        self._runtime = runtime
        self._tool_engine = tool_engine
        self._tool_message_builder = tool_message_builder

    async def stream(
        self,
        context: RuntimeContext,
    ) -> AsyncIterator[Any]:
        """Stream chat response chunks from the runtime executor."""
        async for chunk in self._runtime.stream(context):
            yield chunk

    def _tool_call_signature(
        self,
        call: ToolCall,
    ) -> tuple:
        """Return a stable hashable signature for a tool call used for dedup detection."""
        return (call.name, tuple(sorted(call.arguments.items())))

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        """Execute request against provider and recursively resolve requested tool calls up to MAX_TOOL_ITERATIONS."""
        response = await self._runtime.execute(context)
        tool_call_count = 0
        identical_tool_call_counts: dict[str, int] = {}

        for _iteration in range(settings.MAX_TOOL_ITERATIONS):
            if not response.tool_calls:
                return response

            requested_tool_calls = len(response.tool_calls)

            if (
                tool_call_count + requested_tool_calls
                > settings.MAX_TOOL_CALLS_PER_REQUEST
            ):
                logger.warning(
                    "AgentExecutor reached MAX_TOOL_CALLS_PER_REQUEST={} "
                    "with requested_tool_calls={}. Returning last response.",
                    settings.MAX_TOOL_CALLS_PER_REQUEST,
                    requested_tool_calls,
                )
                return response

            tool_call_count += requested_tool_calls

            for call in response.tool_calls:
                signature = self._tool_call_signature(call)
                count = identical_tool_call_counts.get(signature, 0) + 1

                if count > settings.MAX_IDENTICAL_TOOL_CALLS:
                    logger.warning(
                        "AgentExecutor detected repeated tool call name={} "
                        "count={} limit={}. Returning last response.",
                        call.name,
                        count,
                        settings.MAX_IDENTICAL_TOOL_CALLS,
                    )
                    return response

                identical_tool_call_counts[signature] = count

            context.messages.append(
                AssistantMessage(
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            results = await self._tool_engine.execute(response)

            context.messages.extend(self._tool_message_builder.build(results))

            response = await self._runtime.execute(context)

        # Max iterations reached — return the last response rather than crashing.
        # Log a warning so the operator knows this happened.
        logger.warning(
            f"AgentExecutor reached MAX_TOOL_ITERATIONS={settings.MAX_TOOL_ITERATIONS}. "
            "Returning last partial response."
        )
        return response
