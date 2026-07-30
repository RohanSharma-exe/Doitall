from doitall.models.memory import Memory
from doitall.runtime.memory_filter import MemoryFilter


def test_allow():
    memory_filter = MemoryFilter(min_length=5, max_length=10000)

    assert memory_filter.allow(
        Memory(content="Hello World"),
    )


def test_reject_short():
    memory_filter = MemoryFilter(min_length=10, max_length=10000)

    assert not memory_filter.allow(
        Memory(content="Hi"),
    )


def test_reject_empty():
    memory_filter = MemoryFilter(min_length=5, max_length=10000)

    assert not memory_filter.allow(
        Memory(content=""),
    )


def test_reject_duplicates():
    memory_filter = MemoryFilter(min_length=5, max_length=10000)

    memory = Memory(content="Hello World")
    assert memory_filter.allow(memory)
    assert not memory_filter.allow(memory)  # Second call should reject duplicate
