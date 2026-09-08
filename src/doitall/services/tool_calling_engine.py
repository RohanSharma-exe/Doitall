"""Tool calling execution engine."""

import asyncio
import time

from loguru import logger

from doitall.config.settings import settings
from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import (
    ToolCall,
    ToolExecutionMetadata,
    ToolResult,
)
from doitall.skills.manager import SkillManager


class ToolCallingEngine:
    """Executes tool calls returned by an LLM."""

    def __init__(
        self,
        skill_manager: SkillManager,
    ) -> None:
        """Initialize the tool calling engine."""
        self._skill_manager = skill_manager

    async def execute(
        self,
        response: ProviderResponse,
    ) -> list[ToolResult]:
        """Execute tool calls concurrently with a configurable concurrency limit.

        A failure or timeout in one tool call does not prevent remaining
        tool calls from executing. Failed calls are converted into
        ToolResult objects so the agent can report the failure back
        to the LLM.
        """
        if not response.tool_calls:
            return []

        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TOOL_CALLS)

        return list(
            await asyncio.gather(
                *(
                    self._execute_with_limit(
                        call,
                        semaphore,
                    )
                    for call in response.tool_calls
                )
            )
        )

    async def _execute_with_limit(
        self,
        call: ToolCall,
        semaphore: asyncio.Semaphore,
    ) -> ToolResult:
        """Execute one tool call while respecting the concurrency limit."""
        async with semaphore:
            return await self._execute_single(call)

    async def _execute_single(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """Execute one tool call with timeout and failure isolation."""
        start = time.perf_counter()

        try:
            value = await asyncio.wait_for(
                self._skill_manager.execute(
                    call.name,
                    **call.arguments,
                ),
                timeout=settings.TOOL_EXECUTION_TIMEOUT_SECONDS,
            )

            duration_ms = (time.perf_counter() - start) * 1000

            metadata = ToolExecutionMetadata(
                status="success",
                duration_ms=duration_ms,
            )

            logger.bind(
                tool_name=call.name,
                tool_call_id=call.id,
                status=metadata.status,
                duration_ms=metadata.duration_ms,
            ).info("Tool execution completed")

            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                result=value,
                metadata=metadata,
            )

        except TimeoutError:
            duration_ms = (time.perf_counter() - start) * 1000

            metadata = ToolExecutionMetadata(
                status="timeout",
                duration_ms=duration_ms,
                error="timeout",
            )

            logger.bind(
                tool_name=call.name,
                tool_call_id=call.id,
                status=metadata.status,
                duration_ms=metadata.duration_ms,
            ).warning(
                "Tool execution timed out timeout={}s",
                settings.TOOL_EXECUTION_TIMEOUT_SECONDS,
            )

            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                result=(
                    "Tool execution timed out after "
                    f"{settings.TOOL_EXECUTION_TIMEOUT_SECONDS} seconds."
                ),
                metadata=metadata,
            )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000

            metadata = ToolExecutionMetadata(
                status="error",
                duration_ms=duration_ms,
                error=str(exc),
            )

            logger.bind(
                tool_name=call.name,
                tool_call_id=call.id,
                status=metadata.status,
                duration_ms=metadata.duration_ms,
            ).warning(
                "Tool execution failed error={}",
                exc,
            )

            return ToolResult(
                tool_call_id=call.id,
                name=call.name,
                result=f"Tool execution failed: {exc}",
                metadata=metadata,
            )
