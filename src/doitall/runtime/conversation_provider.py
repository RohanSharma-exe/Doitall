from doitall.runtime.context import RuntimeContext
from doitall.services.conversation_service import ConversationService


class ConversationProvider:
    def __init__(
        self,
        conversation: ConversationService,
    ) -> None:
        self._conversation = conversation

    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        context.messages = self._conversation.messages()
