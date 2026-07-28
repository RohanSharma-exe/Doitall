from doitall.models.message import UserMessage
from doitall.models.session import Session


def test_session_defaults():
    session = Session()

    assert session.title == "New Chat"
    assert session.conversation.messages == []
    assert session.metadata == {}
    assert session.id is not None
    assert session.created_at is not None
    assert session.updated_at is not None


def test_session_conversation():
    session = Session()

    session.conversation.add(UserMessage(content="Hello"))

    assert len(session.conversation.messages) == 1
    assert session.conversation.last().content == "Hello"
