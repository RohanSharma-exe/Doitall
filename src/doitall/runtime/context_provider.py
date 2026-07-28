from typing import Protocol

from doitall.runtime.context import RuntimeContext


class ContextProvider(Protocol):
    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None: ...
