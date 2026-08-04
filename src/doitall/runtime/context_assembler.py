"""Context assembler orchestration module."""

from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider


class ContextAssembler:
    """Assembles runtime context by delegating to multiple context providers.

    The ContextAssembler coordinates multiple context providers to populate
    the RuntimeContext with relevant information from different sources.
    """

    def __init__(
        self,
        providers: list[ContextProvider],
    ) -> None:
        """Initialize the context assembler with a list of providers.

        Args:
            providers: List of context providers to use for context assembly.
        """
        self._providers: tuple[ContextProvider, ...] = tuple(providers)

    async def assemble(
        self,
        query: str,
        *,
        provider: str | None = None,
        model: str | None = None,
    ) -> RuntimeContext:
        """Assemble the runtime context by calling all providers.

        Args:
            query: The user's query to use for context assembly.

        Returns:
            A populated RuntimeContext with information from all providers.
        """
        context = RuntimeContext(
            query=query,
            provider=provider,
            model=model,
        )

        for context_provider in self._providers:
            await context_provider.populate(context)

        return context
