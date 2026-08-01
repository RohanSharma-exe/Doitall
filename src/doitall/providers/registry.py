from loguru import logger

from doitall.config.settings import settings
from doitall.providers.anthropic import AnthropicProvider
from doitall.providers.gemini import GeminiProvider
from doitall.providers.groq import GroqProvider
from doitall.providers.manager import ProviderManager
from doitall.providers.ollama import OllamaProvider
from doitall.providers.openai import OpenAIProvider
from doitall.providers.openrouter import OpenrouterProvider


def register_providers(manager: ProviderManager) -> None:
    """Register all providers whose API keys are configured.

    Providers without a key are skipped and logged at DEBUG level so the
    operator has visibility without noise in normal operation.
    """
    _candidates: list[tuple[str, str, type]] = [
        ("gemini", settings.GEMINI_API_KEY, GeminiProvider),
        ("groq", settings.GROQ_API_KEY, GroqProvider),
        ("openai", settings.OPENAI_API_KEY, OpenAIProvider),
        ("anthropic", settings.ANTHROPIC_API_KEY, AnthropicProvider),
        ("openrouter", settings.OPENROUTER_API_KEY, OpenrouterProvider),
    ]

    registered_any = False

    for name, key, provider_cls in _candidates:
        if key:
            manager.register(provider_cls())
            logger.debug(f"Registered provider: {name}")
            registered_any = True
        else:
            logger.debug(f"Skipping provider '{name}': no API key configured.")

    # Ollama is local — no key needed; register if a base URL is set.
    if settings.OLLAMA_BASE_URL:
        manager.register(OllamaProvider())
        logger.debug("Registered provider: ollama")
        registered_any = True

    if not registered_any:
        logger.warning(
            "No AI providers were registered. "
            "Set at least one provider API key in your .env file."
        )
