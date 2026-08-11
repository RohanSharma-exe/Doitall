"""Tool calling execution engine."""

from loguru import logger

from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolResult
from doitall.services.tool_executor import ToolExecutor


class ToolCallingEngine:
    """Executes tool calls returned by an LLM."""

    def __init__(
        self,
        executor: ToolExecutor,
    ) -> None:
        """Initialize the tool calling engine."""
        self._executor = executor

    async def execute(
        self,
        response: ProviderResponse,
    ) -> list[ToolResult]:
        """Execute all requested tool calls independently.

        A failure in one tool call does not prevent remaining tool calls
        from executing. Failed calls are converted into ToolResult objects
        so the agent can report the failure back to the LLM.
        """
        results: list[ToolResult] = []

        for call in response.tool_calls:
            try:
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

            except Exception as exc:
                logger.warning(
                    "Tool execution failed name={} tool_call_id={} error={}",
                    call.name,
                    call.id,
                    exc,
                )

                results.append(
                    ToolResult(
                        tool_call_id=call.id,
                        name=call.name,
                        result=f"Tool execution failed: {exc}",
                    ),
                )

        return results
