import pytest
from pydantic import ValidationError

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
    message = ToolMessage(content="Tool executed.")

    assert message.role == MessageRole.TOOL


def test_empty_content():
    with pytest.raises(ValidationError):
        UserMessage(content="")
