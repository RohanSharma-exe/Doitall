from doitall.models.tool_call import ToolExecutionMetadata
from doitall.models.message import ToolMessage
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

def test_tool_message_preserves_execution_metadata() -> None:
    service = ConversationService()

    metadata = ToolExecutionMetadata(
        status="success",
        duration_ms=8.25,
    )

    message = ToolMessage(
        content="42",
        tool_call_id="tool-1",
        name="calculator",
        execution_metadata=metadata,
    )

    service.add_message(message)

    stored = service.last_message()

    assert isinstance(stored, ToolMessage)
    assert stored.execution_metadata == metadata
    assert stored.execution_metadata.status == "success"
    assert stored.execution_metadata.duration_ms == 8.25
