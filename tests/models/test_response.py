from doitall.models.response import Response
from doitall.models.usage import Usage


def test_response_defaults():
    response = Response()

    assert response.content == ""
    assert response.model == ""
    assert response.provider == ""


def test_response_usage():
    usage = Usage(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        input_cost=0.01,
        output_cost=0.02,
        total_cost=0.03,
    )

    response = Response(
        content="Hello",
        model="gemini-2.5-flash",
        provider="gemini",
        usage=usage,
    )

    assert response.usage.total_tokens == 30
    assert response.usage.total_cost == 0.03
