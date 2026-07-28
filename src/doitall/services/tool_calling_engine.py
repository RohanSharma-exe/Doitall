from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolResult
from doitall.services.tool_executor import ToolExecutor


class ToolCallingEngine:
    """Executes tool calls returned by an LLM."""

    def __init__(
        self,
        executor: ToolExecutor,
    ) -> None:
        self._executor = executor

    async def execute(
        self,
        response: ProviderResponse,
    ) -> list[ToolResult]:
        """Execute all requested tool calls."""

        results: list[ToolResult] = []

        for call in response.tool_calls:
            value = await self._executor.execute(
                call.name,
                call.arguments,
            )

            results.append(
                ToolResult(
                    tool_call_id=call.id,
                    name=call.name,
                    result=value,
                ),
            )

        return results
