from doitall.models.message import (
    AssistantMessage,
    MessageRole,
    SystemMessage,
    ToolMessage,
    UserMessage,
)


def test_user_message():
    message = UserMessage(content="Hello")

    assert message.role == MessageRole.USER
    assert message.content == "Hello"


def test_assistant_message():
    message = AssistantMessage(content="Hi")

    assert message.role == MessageRole.ASSISTANT


def test_system_message():
    message = SystemMessage(content="You are helpful.")

    assert message.role == MessageRole.SYSTEM


def test_tool_message():
    message = ToolMessage(
        tool_call_id="tool-1",
        name="calculator",
        content="Tool executed.",
    )

    assert message.role == MessageRole.TOOL


def test_assistant_tool_call_can_have_empty_content():
    message = AssistantMessage(
        content="",
        tool_calls=[],
    )

    assert message.content == ""
