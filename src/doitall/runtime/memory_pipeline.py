from doitall.memory.manager import MemoryManager
from doitall.models.message import AssistantMessage, UserMessage
from doitall.runtime.memory_extractor import MemoryExtractor
from doitall.runtime.memory_filter import MemoryFilter
from doitall.runtime.memory_scorer import MemoryScorer


class MemoryPipeline:
    def __init__(
        self,
        manager: MemoryManager,
        extractor: MemoryExtractor,
        memory_filter: MemoryFilter,
        scorer: MemoryScorer,
    ) -> None:
        self._manager = manager
        self._extractor = extractor
        self._filter = memory_filter
        self._scorer = scorer

    async def process(
        self,
        user: UserMessage,
        assistant: AssistantMessage,
    ) -> None:
        memories = self._extractor.extract(
            user,
            assistant,
        )

        for memory in memories:
            if not self._filter.allow(memory):
                continue

            memory = self._scorer.score(memory)

            self._manager.add(memory)
