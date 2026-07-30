from doitall.models.message import AssistantMessage, UserMessage
from doitall.runtime.memory_extractor import MemoryExtractor


def test_extract():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        UserMessage(content="Hello"),
        AssistantMessage(content="Hi"),
    )

    assert len(memories) == 1
    assert memories[0].content == ("User: Hello\nAssistant: Hi")


def test_empty():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        UserMessage(content=""),
        AssistantMessage(content=""),
    )

    assert memories == []
