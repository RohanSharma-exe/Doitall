"""Tool calling execution engine."""

import asyncio

from loguru import logger

from doitall.config.settings import settings
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall, ToolResult
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
        """Execute all requested tool calls concurrently.

        A failure or timeout in one tool call does not prevent remaining
        tool calls from executing. Failed calls are converted into
        ToolResult objects so the agent can report the failure back
        to the LLM.
        """
        tasks = [self._execute_single(call) for call in response.tool_calls]

        if not tasks:
            return []

        return list(await asyncio.gather(*tasks))

    async def _execute_single(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """Execute one tool call with timeout and failure isolation."""
        try:
            value = await asyncio.wait_for(
                self._executor.execute(
                    call.name,
                    call.arguments,
                ),
                timeout=settings.TOOL_EXECUTION_TIMEOUT_SECONDS,
            )

            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                result=value,
            )

        except TimeoutError:
            logger.warning(
                "Tool execution timed out name={} tool_call_id={} timeout={}s",
                call.name,
                call.id,
                settings.TOOL_EXECUTION_TIMEOUT_SECONDS,
            )

            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                result=(
                    "Tool execution timed out after "
                    f"{settings.TOOL_EXECUTION_TIMEOUT_SECONDS} seconds."
                ),
            )

        except Exception as exc:
            logger.warning(
                "Tool execution failed name={} tool_call_id={} error={}",
                call.name,
                call.id,
                exc,
            )

            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                result=f"Tool execution failed: {exc}",
            )
