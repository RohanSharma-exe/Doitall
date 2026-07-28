from doitall.runtime.context import RuntimeContext


def test_runtime_context_defaults():
    context = RuntimeContext()

    assert context.messages == []
    assert context.memories == []
    assert context.knowledge == []
