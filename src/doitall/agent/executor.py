from doitall.models.provider_response import ProviderResponse
from doitall.runtime.context import RuntimeContext
from doitall.runtime.executor import RuntimeExecutor


class AgentExecutor:
    """Coordinates agent execution."""

    def __init__(
        self,
        runtime: RuntimeExecutor,
    ) -> None:
        self._runtime = runtime

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        return await self._runtime.execute(context)
