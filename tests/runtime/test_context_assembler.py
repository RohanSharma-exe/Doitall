from unittest.mock import Mock

from doitall.knowledge.document import Document
from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_assembler import ContextAssembler
from doitall.runtime.conversation_provider import ConversationProvider
from doitall.runtime.knowledge_provider import KnowledgeProvider
from doitall.runtime.memory_provider import MemoryProvider
from doitall.services.conversation_service import ConversationService


class FirstProvider:
    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        context.messages.append(query)


class SecondProvider:
    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        context.memories.append(query)


class OrderProvider:
    def __init__(self, calls: list[str], name: str) -> None:
        self._calls = calls
        self._name = name

    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        self._calls.append(self._name)


class ContextIdProvider:
    def __init__(self) -> None:
        self.contexts: list[RuntimeContext] = []

    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        self.contexts.append(context)


def test_multiple_providers():
    assembler = ContextAssembler(
        [
            FirstProvider(),
            SecondProvider(),
        ]
    )

    context = assembler.assemble("hello")

    assert context.messages == ["hello"]
    assert context.memories == ["hello"]


def test_provider_order():
    calls: list[str] = []

    assembler = ContextAssembler(
        [
            OrderProvider(calls, "first"),
            OrderProvider(calls, "second"),
            OrderProvider(calls, "third"),
        ]
    )

    assembler.assemble("hello")

    assert calls == ["first", "second", "third"]


def test_same_context_passed():
    provider = ContextIdProvider()

    assembler = ContextAssembler(
        [
            provider,
            provider,
        ]
    )

    assembler.assemble("hello")

    assert provider.contexts[0] is provider.contexts[1]


def test_new_context_each_call():
    provider = ContextIdProvider()

    assembler = ContextAssembler([provider])

    assembler.assemble("one")
    assembler.assemble("two")

    assert provider.contexts[0] is not provider.contexts[1]


def test_all_providers_work_together():
    conversation = ConversationService()

    memory = Mock()
    memory.search.return_value = []

    knowledge = Mock()
    knowledge.search.return_value = [
        Document(
            content="Python",
        )
    ]

    assembler = ContextAssembler(
        [
            ConversationProvider(conversation),
            MemoryProvider(memory),
            KnowledgeProvider(knowledge),
        ]
    )

    context = assembler.assemble("python")

    assert context.messages == []
    assert context.memories == []
    assert len(context.knowledge) == 1
    assert context.knowledge[0].content == "Python"
