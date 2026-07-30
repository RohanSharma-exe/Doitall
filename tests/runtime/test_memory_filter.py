from doitall.models.memory import Memory
from doitall.runtime.memory_filter import MemoryFilter


def test_allow():
    memory_filter = MemoryFilter()

    assert memory_filter.allow(
        Memory(content="Hello"),
    )
