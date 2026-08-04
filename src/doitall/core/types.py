"""Core enumeration types for environment levels and supported LLM providers."""

from enum import StrEnum


class Environment(StrEnum):
    """Supported deployment environment levels."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ProviderType(StrEnum):
    """Supported LLM provider type string identifiers."""

    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"

