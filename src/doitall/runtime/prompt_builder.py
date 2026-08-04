"""Prompt builder module combining system instructions, memories, knowledge, and history."""

from doitall.agent.manager import AgentManager
from doitall.models.message import Message, SystemMessage
from doitall.runtime.constants import (
    KNOWLEDGE_HEADER,
    MEMORY_HEADER,
    UNTRUSTED_CONTEXT_INSTRUCTIONS,
)
from doitall.runtime.context import RuntimeContext


class PromptBuilder:
    """Builds prompts for LLM providers from runtime context.

    The PromptBuilder constructs the final message sequence by combining
    system prompts, memories, knowledge, and conversation history.
    """

    def __init__(
        self,
        agent: AgentManager,
    ) -> None:
        """Initialize the prompt builder.

        Args:
            agent: The agent manager containing system prompt configuration.
        """
        self._agent = agent

    def build(
        self,
        context: RuntimeContext,
    ) -> list[Message]:
        """Build the complete message sequence for the LLM.

        Args:
            context: The runtime context with all relevant information.

        Returns:
            List of messages formatted for the LLM provider.
        """
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
        """Add the system prompt if configured.

        Args:
            messages: The message list to append to.
        """
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
        """Add relevant memories to the context.

        Args:
            messages: The message list to append to.
            context: The runtime context containing memories.
        """
        if not context.memories:
            return

        memory_text = "\n".join(
            f"<memory>\n{memory.content}\n</memory>" for memory in context.memories
        )

        messages.append(
            SystemMessage(
                content=f"{UNTRUSTED_CONTEXT_INSTRUCTIONS}{MEMORY_HEADER}{memory_text}",
            )
        )

    def _add_knowledge(
        self,
        messages: list[Message],
        context: RuntimeContext,
    ) -> None:
        """Add relevant knowledge documents to the context.

        Args:
            messages: The message list to append to.
            context: The runtime context containing knowledge.
        """
        if not context.knowledge:
            return

        knowledge_text = "\n".join(
            f"<document>\n{document.content}\n</document>"
            for document in context.knowledge
        )

        messages.append(
            SystemMessage(
                content=f"{UNTRUSTED_CONTEXT_INSTRUCTIONS}{KNOWLEDGE_HEADER}{knowledge_text}",
            )
        )
