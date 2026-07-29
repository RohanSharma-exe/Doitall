from doitall.models.provider_response import ProviderResponse
from doitall.providers.manager import ProviderManager
from doitall.runtime.context import RuntimeContext
from doitall.runtime.prompt_builder import PromptBuilder


class RuntimeExecutor:
    """Executes a single request against the configured provider."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        provider_manager: ProviderManager,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._provider_manager = provider_manager

    def prepare(
        self,
        context: RuntimeContext,
    ) -> list:
        return self._prompt_builder.build(context)

    async def execute(
        self,
        context: RuntimeContext,
    ) -> ProviderResponse:
        messages = self.prepare(context)

        provider = self._provider_manager.default()

        payload = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        return await provider.chat(payload, tools=context.tools)
