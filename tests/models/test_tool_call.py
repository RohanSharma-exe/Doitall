from doitall.models.tool_call import (
    ToolCall,
    ToolResult,
)


def test_tool_call():
    call = ToolCall(
        id="1",
        name="calculator",
        arguments={
            "expression": "2+2",
        },
    )

    assert call.name == "calculator"
    assert call.arguments["expression"] == "2+2"


def test_tool_result():
    result = ToolResult(
        tool_call_id="1",
        name="calculator",
        result=4,
    )

    assert result.result == 4
