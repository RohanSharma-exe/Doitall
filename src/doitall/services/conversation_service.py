from doitall.models.conversation import Conversation
from doitall.models.message import Message


class ConversationService:
    def __init__(
        self,
        conversation: Conversation | None = None,
    ) -> None:
        self._conversation = conversation or Conversation()

    @property
    def conversation(self) -> Conversation:
        return self._conversation

    def add_message(
        self,
        message: Message,
    ) -> None:
        self._conversation.messages.append(message)

    def messages(self) -> list[Message]:
        return list(self._conversation.messages)

    def clear(self) -> None:
        self._conversation.messages.clear()

    def last_message(self) -> Message | None:
        if not self._conversation.messages:
            return None

        return self._conversation.messages[-1]
