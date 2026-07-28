from doitall.models.message import UserMessage
from doitall.runtime.context_builder import ContextBuilder


def test_add_messages():
    builder = ContextBuilder()

    context = builder.add_messages([UserMessage(content="Hello")]).build()

    assert len(context.messages) == 1


def test_builder_returns_self():
    builder = ContextBuilder()

    assert builder.add_messages([]) is builder
    assert builder.add_memories([]) is builder
    assert builder.add_knowledge([]) is builder
