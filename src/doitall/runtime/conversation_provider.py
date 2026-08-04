"""Conversation history context provider module."""

from doitall.runtime.context import RuntimeContext
from doitall.services.conversation_service import ConversationService


class ConversationProvider:
    """Populates RuntimeContext with history messages from ConversationService."""

    def __init__(
        self,
        conversation: ConversationService,
    ) -> None:
        """Initialize provider with ConversationService dependency."""
        self._conversation = conversation

    async def populate(
        self,
        context: RuntimeContext,
    ) -> None:
        """Retrieve conversation messages and assign to context."""
        context.messages = self._conversation.context_messages()

