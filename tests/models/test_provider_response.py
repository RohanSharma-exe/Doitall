from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall


def test_provider_response():
    response = ProviderResponse(
        content="Calculating...",
        tool_calls=[
            ToolCall(
                name="calculator",
                arguments={
                    "expression": "2+2",
                },
            ),
        ],
        finish_reason="tool_calls",
        model="gemini",
    )

    assert response.content == "Calculating..."
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "calculator"
