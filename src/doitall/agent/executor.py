from loguru import logger

from doitall.models.message import AssistantMessage
from doitall.models.provider_response import ProviderResponse
from doitall.runtime.context import RuntimeContext
from doitall.runtime.executor import RuntimeExecutor
from doitall.runtime.tool_message_builder import ToolMessageBuilder
from doitall.services.tool_calling_engine import ToolCallingEngine


class AgentExecutor:
    MAX_TOOL_ITERATIONS = 10

    def __init__(
        self,
        runtime: RuntimeExecutor,
        tool_engine: ToolCallingEngine,
        tool_message_builder: ToolMessageBuilder,
    ) -> None:
        self._runtime = runtime
        self._tool_engine = tool_engine
        self._tool_message_builder = tool_message_builder

    async def stream(
        self,
        context: RuntimeContext,
    ):
        async for chunk in self._runtime.stream(context):
            yield chunk

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        response = await self._runtime.execute(context)

        for _iteration in range(self.MAX_TOOL_ITERATIONS):
            if not response.tool_calls:
                return response

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
            f"AgentExecutor reached MAX_TOOL_ITERATIONS={self.MAX_TOOL_ITERATIONS}. "
            "Returning last partial response."
        )
        return response

