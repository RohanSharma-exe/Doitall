from doitall.agent.manager import AgentManager
from doitall.models.message import SystemMessage
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
    ) -> list:
        messages = []

        if self._agent.system_prompt:
            messages.append(
                SystemMessage(
                    content=self._agent.system_prompt,
                )
            )

        if context.memories:
            memory_text = "\n".join(memory.content for memory in context.memories)

            messages.append(
                SystemMessage(
                    content=f"Relevant memories:\n{memory_text}",
                )
            )

        if context.knowledge:
            knowledge_text = "\n".join(
                document.content for document in context.knowledge
            )

            messages.append(
                SystemMessage(
                    content=f"Relevant knowledge:\n{knowledge_text}",
                )
            )

        messages.extend(context.messages)

        return messages
