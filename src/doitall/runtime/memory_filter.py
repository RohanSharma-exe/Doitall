"""Memory filtering and deduplication module."""

from collections import deque

from doitall.models.memory import Memory


class MemoryFilter:
    """Filters memories based on length thresholds and duplicate detection cache."""

    def __init__(
        self,
        min_length: int = 10,
        max_length: int = 10000,
        dedup_cache_size: int = 500,
    ) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.dedup_cache_size = dedup_cache_size
        self._seen_order: deque[str] = deque(maxlen=dedup_cache_size)
        self._seen_contents: set[str] = set()

    def allow(
        self,
        memory: Memory,
    ) -> bool:
        """Check if a memory should be stored based on filtering criteria."""

        content = memory.content.strip()
        if len(content) < self.min_length:
            return False

        if len(content) > self.max_length:
            return False

        content_normalized = content.lower().strip()
        if content_normalized in self._seen_contents:
            return False

        if self.dedup_cache_size <= 0:
            return True

        if len(self._seen_order) == self._seen_order.maxlen:
            oldest = self._seen_order.popleft()
            self._seen_contents.discard(oldest)

        self._seen_order.append(content_normalized)
        self._seen_contents.add(content_normalized)

        return True

    def clear_cache(self) -> None:
        """Clear the duplicate detection cache."""
        self._seen_order.clear()
        self._seen_contents.clear()
