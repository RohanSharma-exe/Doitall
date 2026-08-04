"""ContextProvider protocol interface module."""

from typing import Protocol

from doitall.runtime.context import RuntimeContext


class ContextProvider(Protocol):
    """Protocol for context providers that enrich a RuntimeContext with additional information.

    Context providers are used to add relevant information to the runtime context,
    such as conversation history, memories, knowledge, and available tools.
    """

    async def populate(
        self,
        context: RuntimeContext,
    ) -> None:
        """Populate the runtime context with relevant information.

        Args:
            context: The runtime context to populate with information.
        """
        ...
