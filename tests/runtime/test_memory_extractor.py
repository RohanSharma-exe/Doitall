from doitall.models.message import AssistantMessage, UserMessage
from doitall.runtime.memory_extractor import MemoryExtractor


def test_extract():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        UserMessage(content="Hello"),
        AssistantMessage(content="Hi"),
    )

    assert len(memories) == 1
    assert memories[0].content == ("User preference/fact: Hello\nAssistant outcome: Hi")


def test_empty():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        UserMessage(content=""),
        AssistantMessage(content=""),
    )

    assert memories == []


def test_extract_compacts_whitespace():
    extractor = MemoryExtractor()

    memories = extractor.extract(
        UserMessage(content="  likes   concise\nanswers  "),
        AssistantMessage(content="  noted   preference  "),
    )

    assert memories[0].content == (
        "User preference/fact: likes concise answers\n"
        "Assistant outcome: noted preference"
    )
