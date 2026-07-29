from doitall.models.tool_call import ToolResult
from doitall.runtime.tool_message_builder import ToolMessageBuilder


def test_build():
    builder = ToolMessageBuilder()

    messages = builder.build(
        [
            ToolResult(
                name="calculator",
                result=42,
            )
        ]
    )

    assert len(messages) == 1
    assert messages[0].content == "42"
