"""Memory processing pipeline module."""

from doitall.memory.manager import MemoryManager
from doitall.models.message import AssistantMessage, UserMessage
from doitall.runtime.memory_extractor import MemoryExtractor
from doitall.runtime.memory_filter import MemoryFilter
from doitall.runtime.memory_scorer import MemoryScorer


class MemoryPipeline:
    """Coordinates memory extraction, filtering, scoring, and storage."""

    def __init__(
        self,
        manager: MemoryManager,
        extractor: MemoryExtractor,
        memory_filter: MemoryFilter,
        scorer: MemoryScorer,
    ) -> None:
        """Initialize memory pipeline with manager, extractor, filter, and scorer."""
        self._manager = manager
        self._extractor = extractor
        self._filter = memory_filter
        self._scorer = scorer

    async def process(
        self,
        user: UserMessage,
        assistant: AssistantMessage,
    ) -> None:
        """Extract, filter, score, and persist memories from user and assistant messages."""
        memories = self._extractor.extract(
            user,
            assistant,
        )

        for memory in memories:
            if not self._filter.allow(memory):
                continue

            memory = self._scorer.score(memory)

            await self._manager.add(memory)
