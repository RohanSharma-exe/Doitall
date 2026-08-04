"""Tool execution result message conversion module."""

from doitall.models.message import ToolMessage
from doitall.models.tool_call import ToolResult


class ToolMessageBuilder:
    """Converts tool results into conversation messages."""

    def build(
        self,
        results: list[ToolResult],
    ) -> list[ToolMessage]:
        """Convert list of ToolResult objects into ToolMessage instances."""
        return [
            ToolMessage(
                tool_call_id=result.tool_call_id,
                name=result.name,
                content=str(result.result),
            )
            for result in results
        ]

