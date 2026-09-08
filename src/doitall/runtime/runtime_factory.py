"""Runtime factory module for constructing ChatService dependency stacks."""

from doitall.agent.agent import Agent
from doitall.agent.executor import AgentExecutor
from doitall.knowledge.repository import KnowledgeRepository
from doitall.memory.manager import MemoryManager
from doitall.memory.store import MemoryStore
from doitall.providers.manager import ProviderManager
from doitall.runtime.context_assembler import ContextAssembler
from doitall.runtime.conversation_provider import ConversationProvider
from doitall.runtime.executor import RuntimeExecutor
from doitall.runtime.knowledge_provider import KnowledgeProvider
from doitall.runtime.memory_extractor import MemoryExtractor
from doitall.runtime.memory_filter import MemoryFilter
from doitall.runtime.memory_pipeline import MemoryPipeline
from doitall.runtime.memory_provider import MemoryProvider
from doitall.runtime.memory_scorer import MemoryScorer
from doitall.runtime.prompt_builder import PromptBuilder
from doitall.runtime.tool_message_builder import ToolMessageBuilder
from doitall.runtime.tool_provider import ToolProvider
from doitall.services.chat_service import ChatService
from doitall.services.conversation_service import ConversationService
from doitall.services.registry import container
from doitall.services.tool_calling_engine import ToolCallingEngine
from doitall.skills.manager import SkillManager


class RuntimeFactory:
    """Creates an isolated runtime ChatService instance for an assistant agent."""

    def create(
        self,
        agent: Agent,
        conversation_service: ConversationService | None = None,
    ) -> ChatService:
        """Construct and wire all services required for agent execution."""

        provider_manager: ProviderManager = container.resolve("provider_manager")
        skill_manager: SkillManager = container.resolve("skill_manager")
        skill_registry = container.resolve("skill_registry")
        memory_store: MemoryStore = container.resolve("memory_store")
        knowledge_repository: KnowledgeRepository = container.resolve(
            "knowledge_repository"
        )

        memory_manager = MemoryManager(memory_store)

        # Use the provided conversation_service (DB-backed) or create a
        # fresh in-memory one for one-shot / test usage.
        conversation = conversation_service or ConversationService()

        prompt_builder = PromptBuilder(agent)
        runtime = RuntimeExecutor(prompt_builder, provider_manager)
        tool_engine = ToolCallingEngine(skill_manager)
        tool_message_builder = ToolMessageBuilder()

        context_assembler = ContextAssembler(
            [
                ConversationProvider(conversation),
                MemoryProvider(memory_manager),
                KnowledgeProvider(knowledge_repository),
                ToolProvider(skill_registry),
            ]
        )

        executor = AgentExecutor(runtime, tool_engine, tool_message_builder)

        memory_pipeline = MemoryPipeline(
            manager=memory_manager,
            extractor=MemoryExtractor(),
            memory_filter=MemoryFilter(min_length=10, max_length=10000),
            scorer=MemoryScorer(base_score=0.5),
        )

        return ChatService(
            conversation_service=conversation,
            context_assembler=context_assembler,
            agent_executor=executor,
            memory_pipeline=memory_pipeline,
        )

