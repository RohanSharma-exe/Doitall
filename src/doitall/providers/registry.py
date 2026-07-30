from doitall.providers.anthropic import AnthropicProvider
from doitall.providers.gemini import GeminiProvider
from doitall.providers.groq import GroqProvider
from doitall.providers.manager import ProviderManager
from doitall.providers.ollama import OllamaProvider
from doitall.providers.openai import OpenAIProvider
from doitall.providers.openrouter import OpenrouterProvider


def register_providers(manager: ProviderManager) -> None:
    """Register all available providers."""

    manager.register(
        GeminiProvider(),
        default=True,
    )

    manager.register(
        GroqProvider(),
    )

    manager.register(
        OpenAIProvider(),
    )

    manager.register(
        AnthropicProvider(),
    )

    manager.register(
        OllamaProvider(),
    )

    manager.register(
        OpenrouterProvider(),
    )
