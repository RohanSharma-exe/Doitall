from doitall.agent.manager import AgentManager
from doitall.models.message import Message, SystemMessage
from doitall.runtime.constants import (
    KNOWLEDGE_HEADER,
    MEMORY_HEADER,
)
from doitall.runtime.context import RuntimeContext


class PromptBuilder:
    def __init__(
        self,
        agent: AgentManager,
    ) -> None:
        self._agent = agent

    def build(
        self,
        context: RuntimeContext,
    ) -> list[Message]:
        messages: list[Message] = []

        self._add_system_prompt(messages)
        self._add_memories(messages, context)
        self._add_knowledge(messages, context)

        messages.extend(context.messages)

        return messages

    def _add_system_prompt(
        self,
        messages: list[Message],
    ) -> None:
        if self._agent.system_prompt:
            messages.append(
                SystemMessage(
                    content=self._agent.system_prompt,
                )
            )

    def _add_memories(
        self,
        messages: list[Message],
        context: RuntimeContext,
    ) -> None:
        if not context.memories:
            return

        memory_text = "\n".join(memory.content for memory in context.memories)

        messages.append(
            SystemMessage(
                content=f"{MEMORY_HEADER}{memory_text}",
            )
        )

    def _add_knowledge(
        self,
        messages: list[Message],
        context: RuntimeContext,
    ) -> None:
        if not context.knowledge:
            return

        knowledge_text = "\n".join(document.content for document in context.knowledge)

        messages.append(
            SystemMessage(
                content=f"{KNOWLEDGE_HEADER}{knowledge_text}",
            )
        )
