from doitall.models.memory import Memory
from doitall.runtime.memory_scorer import MemoryScorer


def test_score():
    scorer = MemoryScorer()

    memory = Memory(
        content="Hello",
        importance=0.1,
    )

    memory = scorer.score(memory)

    assert memory.importance == 0.5
