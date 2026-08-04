"""Memory extraction module for creating memory objects from chat interactions."""

from doitall.models.memory import Memory
from doitall.models.message import AssistantMessage, UserMessage


class MemoryExtractor:
    """Extracts memory payload objects from user-assistant interaction pairs."""

    def extract(
        self,
        user: UserMessage,
        assistant: AssistantMessage,
    ) -> list[Memory]:
        """Extract memory instances from user prompt and assistant response."""
        if not user.content.strip() and not assistant.content.strip():
            return []

        user_content = self._compact(user.content)
        assistant_content = self._compact(assistant.content)
        return [
            Memory(
                content=(
                    f"User preference/fact: {user_content}\nAssistant outcome: {assistant_content}"
                )
            )
        ]

    def _compact(self, content: str, limit: int = 1000) -> str:
        """Keep memory payloads concise and avoid storing bulky raw transcripts."""
        compacted = " ".join(content.split())
        if len(compacted) <= limit:
            return compacted
        return f"{compacted[:limit].rstrip()}…"
