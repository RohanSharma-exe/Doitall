from doitall.models.conversation import Conversation
from doitall.models.message import (
    AssistantMessage,
    UserMessage,
)


def test_conversation_add():
    conversation = Conversation()

    conversation.add(UserMessage(content="Hello"))

    assert len(conversation.messages) == 1
    assert conversation.last().content == "Hello"


def test_conversation_clear():
    conversation = Conversation()

    conversation.add(UserMessage(content="Hello"))

    conversation.add(AssistantMessage(content="Hi"))

    conversation.clear()

    assert len(conversation.messages) == 0
    assert conversation.last() is None
