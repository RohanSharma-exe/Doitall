"""Memory importance scoring heuristic module."""

from doitall.models.memory import Memory


class MemoryScorer:
    """Scores memories based on importance and relevance."""

    def __init__(
        self,
        base_score: float = 0.5,
    ) -> None:
        self.base_score = base_score

    def score(
        self,
        memory: Memory,
    ) -> Memory:
        """Calculate and assign an importance score to a memory."""

        content = memory.content.strip()

        # Base score
        score = self.base_score

        # Increase score for longer, more substantive content
        if len(content) > 100:
            score += 0.1
        if len(content) > 500:
            score += 0.1

        # Increase score for content with question marks (indicating questions)
        if "?" in content:
            score += 0.1

        # Increase score for content with action words
        action_words = ["should", "must", "need to", "have to", "will", "going to"]
        if any(word in content.lower() for word in action_words):
            score += 0.1

        # Decrease score for very short content
        if len(content) < 20:
            score -= 0.2

        # Ensure score is within valid range
        memory.importance = max(0.0, min(1.0, score))

        return memory
