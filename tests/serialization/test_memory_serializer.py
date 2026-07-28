from doitall.models.memory import Memory
from doitall.serialization.memory_serializer import MemorySerializer


def test_memory_serializer_round_trip():
    memory = Memory(
        content="Python",
    )

    payload = MemorySerializer.to_payload(memory)

    restored = MemorySerializer.from_payload(
        memory.id,
        payload,
    )

    assert restored.content == memory.content
    assert restored.id == memory.id
    assert restored.importance == memory.importance
