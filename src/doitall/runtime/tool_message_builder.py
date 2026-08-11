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
        messages: list[ToolMessage] = []

        for result in results:
            if result.tool_call_id is None:
                raise ValueError(
                    f"Tool result for '{result.name}' is missing tool_call_id."
                )

            messages.append(
                ToolMessage(
                    tool_call_id=result.tool_call_id,
                    name=result.name,
                    content=str(result.result),
                )
            )

        return messages
