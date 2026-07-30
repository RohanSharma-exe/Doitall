from doitall.models.memory import Memory


class MemoryScorer:
    def score(
        self,
        memory: Memory,
    ) -> Memory:
        memory.importance = 0.5
        return memory
