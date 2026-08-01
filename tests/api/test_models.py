from doitall.api.models import MessageDetail


def test_message_detail_tool_calls_are_isolated():
    first = MessageDetail(role="assistant", content="", created_at="now")
    second = MessageDetail(role="assistant", content="", created_at="now")

    first.tool_calls.append({"name": "calculator"})

    assert first.tool_calls == [{"name": "calculator"}]
    assert second.tool_calls == []
