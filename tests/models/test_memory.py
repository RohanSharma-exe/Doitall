from doitall.models.memory import Memory


def test_memory_defaults():
    memory = Memory(content="The user likes Python.")

    assert memory.content == "The user likes Python."
    assert memory.source == "conversation"
    assert memory.importance == 0.5
    assert memory.metadata == {}
    assert memory.id is not None
    assert memory.created_at is not None


def test_memory_custom_values():
    memory = Memory(
        content="Uses Gemini.",
        source="profile",
        importance=0.9,
        metadata={
            "user": "rohan",
            "category": "preference",
        },
    )

    assert memory.source == "profile"
    assert memory.importance == 0.9
    assert memory.metadata["user"] == "rohan"
    assert memory.metadata["category"] == "preference"
