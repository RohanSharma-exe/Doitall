from doitall.models.tool_call import ToolExecutionMetadata, ToolResult
from doitall.runtime.tool_message_builder import ToolMessageBuilder


def test_build():
    builder = ToolMessageBuilder()

    messages = builder.build(
        [
            ToolResult(
                tool_call_id="tool-1",
                name="calculator",
                result=42,
            )
        ]
    )

    assert len(messages) == 1
    assert messages[0].content == "42"


def test_build_preserves_execution_metadata() -> None:
    builder = ToolMessageBuilder()

    metadata = ToolExecutionMetadata(
        status="success",
        duration_ms=12.5,
    )

    messages = builder.build(
        [
            ToolResult(
                tool_call_id="tool-1",
                name="calculator",
                result=42,
                metadata=metadata,
            )
        ]
    )

    assert len(messages) == 1
    assert messages[0].execution_metadata == metadata
    assert messages[0].execution_metadata.status == "success"
    assert messages[0].execution_metadata.duration_ms == 12.5
