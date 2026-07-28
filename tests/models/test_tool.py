from doitall.models.tool import (
    Tool,
    ToolParameter,
)


def test_tool():
    tool = Tool(
        name="calculator",
        description="Performs calculations",
        parameters=[
            ToolParameter(
                name="expression",
                type="string",
                description="Math expression",
                required=True,
            )
        ],
    )

    assert tool.name == "calculator"
    assert tool.description == "Performs calculations"
    assert len(tool.parameters) == 1
    assert tool.parameters[0].name == "expression"


def test_tool_without_parameters():
    tool = Tool(
        name="time",
        description="Returns current time",
    )

    assert tool.parameters == []
