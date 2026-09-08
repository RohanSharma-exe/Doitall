"""Automatic provider registration module.

Inspects settings for configured API keys and registers available LLM providers.
"""

import httpx
from loguru import logger

from doitall.config.settings import settings
from doitall.providers.litellm_provider import LiteLLMProvider
from doitall.providers.manager import ProviderManager


def register_providers(manager: ProviderManager) -> None:
    """Register all providers whose API keys are configured.

    Providers without a key are skipped and logged at DEBUG level so the
    operator has visibility without noise in normal operation.
    """
    _candidates: list[tuple[str, str, str]] = [
        ("gemini", settings.GEMINI_API_KEY, settings.GEMINI_MODEL),
        ("groq", settings.GROQ_API_KEY, settings.GROQ_MODEL),
        ("openai", settings.OPENAI_API_KEY, settings.OPENAI_MODEL),
        ("anthropic", settings.ANTHROPIC_API_KEY, settings.ANTHROPIC_MODEL),
        ("openrouter", settings.OPENROUTER_API_KEY, settings.OPENROUTER_MODEL),
        ("nvidia", settings.NVIDIA_API_KEY, settings.NVIDIA_MODEL),
    ]

    registered_any = False

    for name, key, default_model in _candidates:
        if key:
            manager.register(LiteLLMProvider(name, default_model))
            logger.debug(f"Registered provider: {name}")
            registered_any = True
        else:
            logger.debug(f"Skipping provider '{name}': no API key configured.")

    # Ollama is local — no API key; health check hits /api/tags instead of a chat ping.
    if settings.OLLAMA_BASE_URL:
        base_url = settings.OLLAMA_BASE_URL

        async def _ollama_health() -> bool:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{base_url}/api/tags")
                    return resp.status_code == 200
            except Exception:
                return False

        manager.register(
            LiteLLMProvider("ollama", settings.OLLAMA_MODEL, health_check_fn=_ollama_health)
        )
        logger.debug("Registered provider: ollama")
        registered_any = True

    if not registered_any:
        logger.warning(
            "No AI providers were registered. "
            "Set at least one provider API key in your .env file."
        )
