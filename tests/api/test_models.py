from doitall.api.models import ChatRequest, ChatResponse, MessageDetail


def test_message_detail_tool_calls_are_isolated():
    first = MessageDetail(role="assistant", content="", created_at="now")
    second = MessageDetail(role="assistant", content="", created_at="now")

    first.tool_calls.append({"name": "calculator"})

    assert first.tool_calls == [{"name": "calculator"}]
    assert second.tool_calls == []


def test_chat_request_accepts_model_override():
    request = ChatRequest(message="hello", provider="openai", model="gpt-4o-mini")

    assert request.model == "gpt-4o-mini"


def test_chat_response_usage_tokens_are_isolated():
    first = ChatResponse(response="one")
    second = ChatResponse(response="two")

    first.usage_tokens["total"] = 10

    assert first.usage_tokens == {"total": 10}
    assert second.usage_tokens == {}


def test_chat_response_includes_assistant_message_shape():
    response = ChatResponse(response="hello")

    assert response.message == {}

    response = ChatResponse(
        response="hello", message={"role": "assistant", "content": "hello"}
    )

    assert response.message["role"] == "assistant"
    assert response.message["content"] == "hello"
