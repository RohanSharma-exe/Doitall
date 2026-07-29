from doitall.models.tool_definition import ToolDefinition
from doitall.providers.gemini import GeminiProvider


class FakeMessage:
    content = "Hello"


class FakeChoice:
    message = FakeMessage()
    finish_reason = "stop"


class FakeResponse:
    def __init__(self) -> None:
        self.model = "gemini-test"
        self.choices = [FakeChoice()]


def test_to_provider_response():
    provider = GeminiProvider()

    response = provider._to_provider_response(FakeResponse())

    assert response.content == "Hello"
    assert response.finish_reason == "stop"
    assert response.model == "gemini-test"
    assert response.tool_calls == []


def test_convert_tools():
    provider = GeminiProvider()

    tools = [
        ToolDefinition(
            name="calculator",
            description="Calculator",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                    },
                },
                "required": ["expression"],
            },
        )
    ]

    converted = provider._convert_tools(tools)

    assert converted == [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Calculator",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                        },
                    },
                    "required": ["expression"],
                },
            },
        }
    ]


class FakeFunction:
    name = "calculator"
    arguments = '{"expression":"2+2"}'


class FakeToolCall:
    id = "call_1"
    function = FakeFunction()


class FakeToolMessage:
    def __init__(self) -> None:
        self.content = ""
        self.tool_calls = [FakeToolCall()]


def test_parse_tool_calls():
    provider = GeminiProvider()

    tool_calls = provider._parse_tool_calls(
        FakeToolMessage(),
    )

    assert len(tool_calls) == 1

    assert tool_calls[0].id == "call_1"
    assert tool_calls[0].name == "calculator"
    assert tool_calls[0].arguments == {
        "expression": "2+2",
    }
