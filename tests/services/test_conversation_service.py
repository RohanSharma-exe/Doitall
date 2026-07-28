from doitall.models.message import UserMessage
from doitall.services.conversation_service import ConversationService


def test_add_message():
    service = ConversationService()

    service.add_message(UserMessage(content="Hello"))

    assert len(service.messages()) == 1


def test_last_message():
    service = ConversationService()

    message = UserMessage(content="Hi")

    service.add_message(message)

    assert service.last_message() == message


def test_clear():
    service = ConversationService()

    service.add_message(UserMessage(content="Hello"))

    service.clear()

    assert service.messages() == []


def test_messages_returns_copy():
    service = ConversationService()

    service.add_message(UserMessage(content="Hello"))

    messages = service.messages()

    messages.clear()

    assert len(service.messages()) == 1
