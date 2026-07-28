from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ProviderType(StrEnum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
