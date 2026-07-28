from doitall.providers.gemini import GeminiProvider
from doitall.providers.groq import GroqProvider
from doitall.providers.manager import ProviderManager


def register_providers(manager: ProviderManager) -> None:
    """Register all available providers."""

    manager.register(
        GeminiProvider(),
        default=True,
    )

    manager.register(
        GroqProvider(),
    )
