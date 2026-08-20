import pytest
from pydantic import ValidationError

from doitall.api.models import (
    MAX_METADATA_DEPTH,
    MAX_METADATA_KEY_LENGTH,
    MAX_METADATA_SERIALIZED_BYTES,
    ChatRequest,
    ChatResponse,
    IngestRequest,
    MessageDetail,
)


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


def test_ingest_request_accepts_bounded_json_metadata():
    request = IngestRequest(
        content="hello",
        metadata={"source": {"tags": ["docs", 1, True, None]}},
    )

    assert request.metadata["source"]["tags"] == ["docs", 1, True, None]


def test_ingest_request_rejects_oversized_serialized_metadata():
    metadata = {"value": "x" * MAX_METADATA_SERIALIZED_BYTES}

    with pytest.raises(ValidationError, match="serialized metadata may not exceed"):
        _ = IngestRequest(content="hello", metadata=metadata)


def test_ingest_request_rejects_excessive_metadata_depth():
    metadata: dict[str, object] = {"value": "ok"}
    for _ in range(MAX_METADATA_DEPTH):
        metadata = {"nested": metadata}

    with pytest.raises(ValidationError, match="nesting depth may not exceed"):
        _ = IngestRequest(content="hello", metadata=metadata)


def test_ingest_request_rejects_long_nested_metadata_keys():
    metadata = {"nested": {"x" * (MAX_METADATA_KEY_LENGTH + 1): "value"}}

    with pytest.raises(ValidationError, match="key length may not exceed"):
        _ = IngestRequest(content="hello", metadata=metadata)


def test_ingest_request_rejects_non_json_metadata_values():
    with pytest.raises(ValidationError, match="JSON-compatible"):
        _ = IngestRequest(content="hello", metadata={"invalid": ("tuple",)})


def test_ingest_request_rejects_non_finite_metadata_numbers():
    with pytest.raises(ValidationError, match="numbers must be finite"):
        _ = IngestRequest(content="hello", metadata={"invalid": float("inf")})
