from typing import Protocol

from doitall.runtime.context import RuntimeContext


class ContextProvider(Protocol):
    """Enriches a RuntimeContext with additional information."""

    async def populate(
        self,
        context: RuntimeContext,
    ) -> None:
        """Populate the runtime context."""
        ...
