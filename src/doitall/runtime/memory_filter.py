from doitall.models.memory import Memory


class MemoryFilter:
    """Filters memories based on various criteria."""

    def __init__(
        self,
        min_length: int = 10,
        max_length: int = 10000,
    ) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self._seen_contents: set[str] = set()

    def allow(
        self,
        memory: Memory,
    ) -> bool:
        """Check if a memory should be stored based on filtering criteria."""

        # Filter by length
        content = memory.content.strip()
        if len(content) < self.min_length:
            return False

        if len(content) > self.max_length:
            return False

        # Filter out empty or whitespace-only content
        if not content:
            return False

        # Filter out duplicates
        content_normalized = content.lower().strip()
        if content_normalized in self._seen_contents:
            return False

        self._seen_contents.add(content_normalized)

        return True

    def clear_cache(self) -> None:
        """Clear the duplicate detection cache."""
        self._seen_contents.clear()
