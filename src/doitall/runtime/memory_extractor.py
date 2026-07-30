from doitall.models.memory import Memory
from doitall.models.message import AssistantMessage, UserMessage


class MemoryExtractor:
    def extract(
        self,
        user: UserMessage,
        assistant: AssistantMessage,
    ) -> list[Memory]:
        if not user.content.strip() and not assistant.content.strip():
            return []

        return [
            Memory(
                content=(f"User: {user.content}\nAssistant: {assistant.content}"),
            )
        ]
