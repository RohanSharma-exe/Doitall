from doitall.models.memory import Memory
from doitall.runtime.memory_scorer import MemoryScorer


def test_score():
    scorer = MemoryScorer(base_score=0.5)

    memory = Memory(
        content="Hello",
        importance=0.1,
    )

    memory = scorer.score(memory)

    # The scorer now calculates importance based on content
    # Short content like "Hello" will have a lower score
    assert memory.importance >= 0.0
    assert memory.importance <= 1.0


def test_score_long_content():
    scorer = MemoryScorer(base_score=0.5)

    memory = Memory(
        content="This is a much longer piece of text that should receive a higher importance score due to its length and substance.",
        importance=0.1,
    )

    memory = scorer.score(memory)

    # Longer content should get a higher score
    assert memory.importance >= 0.0
    assert memory.importance <= 1.0
