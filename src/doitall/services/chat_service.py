"""ChatService facade orchestrating context assembly, agent execution, and memory pipeline processing."""

from collections.abc import AsyncIterator

from loguru import logger

from doitall.agent.executor import AgentExecutor
from doitall.models.message import AssistantMessage, UserMessage
from doitall.models.provider_response import ProviderResponse
from doitall.runtime.context_assembler import ContextAssembler
from doitall.runtime.memory_pipeline import MemoryPipeline
from doitall.services.conversation_service import ConversationService


class ChatService:
    """Orchestrates end-to-end chat flow for sync, async, and streaming responses."""

    def __init__(
        self,
        conversation_service: ConversationService,
        context_assembler: ContextAssembler,
        agent_executor: AgentExecutor,
        memory_pipeline: MemoryPipeline,
    ) -> None:
        """Initialize ChatService with core runtime dependencies."""
        self._conversation_service = conversation_service
        self._context_assembler = context_assembler
        self._agent_executor = agent_executor
        self._memory_pipeline = memory_pipeline

    async def stream_chat(
        self,
        content: str,
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream LLM chat response chunks while updating conversation history and memory pipeline."""
        user_message = UserMessage(content=content)

        self._conversation_service.add_message(user_message)

        if model:
            context = await self._context_assembler.assemble(
                content, provider=provider, model=model
            )
        else:
            context = await self._context_assembler.assemble(content, provider=provider)
        original_context_length = len(context.messages)

        if context.tools:
            response = await self._agent_executor.execute(context)
            for message in context.messages[original_context_length:]:
                self._conversation_service.add_message(message)
            if response.content:
                yield response.content
            assistant_message = AssistantMessage(
                content=response.content,
                tool_calls=response.tool_calls,
            )
        else:
            response_chunks: list[str] = []
            async for chunk in self._agent_executor.stream(context):
                response_chunks.append(chunk)
                yield chunk

            assistant_message = AssistantMessage(content="".join(response_chunks))
        self._conversation_service.add_message(assistant_message)

        try:
            await self._memory_pipeline.process(user_message, assistant_message)
        except Exception as e:
            logger.warning(f"Memory pipeline failed (non-fatal): {e}")

    async def chat(
        self,
        content: str,
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> str:
        response = await self.chat_response(content, provider=provider, model=model)
        return response.content

    async def chat_response(
        self,
        content: str,
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> ProviderResponse:
        user_message = UserMessage(
            content=content,
        )

        self._conversation_service.add_message(
            user_message,
        )

        if provider:
            context = await self._context_assembler.assemble(
                content,
                provider=provider,
                model=model,
            )
        else:
            if model:
                context = await self._context_assembler.assemble(
                    content,
                    model=model,
                )
            else:
                context = await self._context_assembler.assemble(
                    content,
                )

        original_context_length = len(context.messages)

        response = await self._agent_executor.execute(
            context,
        )

        for message in context.messages[original_context_length:]:
            self._conversation_service.add_message(message)

        if response.usage_tokens:
            logger.debug(
                "LLM token usage provider={} model={} usage={}",
                provider or "default",
                response.model,
                response.usage_tokens,
            )

        assistant_message = AssistantMessage(
            content=response.content,
            tool_calls=response.tool_calls,
        )

        self._conversation_service.add_message(
            assistant_message,
        )

        try:
            await self._memory_pipeline.process(
                user_message,
                assistant_message,
            )
        except Exception as e:
            # Memory storage is best-effort — a failure must never
            # prevent the user from receiving the LLM's response.
            logger.warning(f"Memory pipeline failed (non-fatal): {e}")

        return response
