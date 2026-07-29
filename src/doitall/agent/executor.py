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

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        response = await self._runtime.execute(context)

        iterations = 0

        while response.tool_calls:
            if iterations >= self.MAX_TOOL_ITERATIONS:
                raise RuntimeError("Maximum tool iterations exceeded.")

            iterations += 1

            results = await self._tool_engine.execute(response)

            context.messages.extend(self._tool_message_builder.build(results))

            response = await self._runtime.execute(context)

        return response
