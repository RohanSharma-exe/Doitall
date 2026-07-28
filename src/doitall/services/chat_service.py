from doitall.agent.executor import AgentExecutor
from doitall.models.message import Message, MessageRole
from doitall.runtime.context_assembler import ContextAssembler
from doitall.services.conversation_service import ConversationService


class ChatService:
    def __init__(
        self,
        conversation_service: ConversationService,
        context_assembler: ContextAssembler,
        agent_executor: AgentExecutor,
    ) -> None:
        self._conversation_service = conversation_service
        self._context_assembler = context_assembler
        self._agent_executor = agent_executor

    async def chat(
        self,
        content: str,
    ) -> str:
        user_message = Message(
            role=MessageRole.USER,
            content=content,
        )

        self._conversation_service.add_message(user_message)

        context = self._context_assembler.assemble(content)

        response = await self._agent_executor.execute(context)

        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response.content,
        )

        self._conversation_service.add_message(
            assistant_message,
        )

        return response.content
