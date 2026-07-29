from doitall.runtime.context import RuntimeContext
from doitall.runtime.context_provider import ContextProvider
from doitall.skills.registry import SkillRegistry


class ToolProvider(ContextProvider):
    """Adds registered tool definitions to the runtime context."""

    def __init__(
        self,
        registry: SkillRegistry,
    ) -> None:
        self._registry = registry

    def populate(
        self,
        context: RuntimeContext,
        query: str,
    ) -> None:
        context.tools.extend(
            self._registry.definitions(),
        )
