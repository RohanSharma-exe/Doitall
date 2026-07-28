from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider


class ContextAssembler:
    def __init__(
        self,
        providers: list[ContextProvider],
    ) -> None:
        self._providers = providers

    def assemble(
        self,
        query: str,
    ) -> RuntimeContext:
        context = RuntimeContext()

        for provider in self._providers:
            provider.populate(context, query)

        return context
