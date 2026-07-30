from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider


class ContextAssembler:
    def __init__(
        self,
        providers: list[ContextProvider],
    ) -> None:
        self._providers: tuple[ContextProvider, ...] = tuple(providers)

    async def assemble(
        self,
        query: str,
    ) -> RuntimeContext:
        context = RuntimeContext(
            query=query,
        )

        for provider in self._providers:
            await provider.populate(context)

        return context
