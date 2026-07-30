import pytest

from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_assembler import ContextAssembler


class DummyProvider:
    async def populate(self, context: RuntimeContext) -> None:
        context.metadata["called"] = True


@pytest.mark.asyncio
async def test_context_assembler_calls_providers() -> None:
    assembler = ContextAssembler(
        providers=[
            DummyProvider(),
        ]
    )

    context = await assembler.assemble("hello")

    assert context.metadata["called"] is True


@pytest.mark.asyncio
async def test_context_starts_empty() -> None:
    assembler = ContextAssembler([])

    context = await assembler.assemble("hello")

    assert context.messages == []
    assert context.memories == []
    assert context.knowledge == []
    assert context.tools == []
