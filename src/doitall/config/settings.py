"""Application configuration settings module.

Loads environment variables and `.env` file configurations using Pydantic Settings.
Provides cached access to global `settings` instance.
"""

from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import Field, PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Runtime files default to the launch directory, never the installed package tree.
BASE_DIR = Path.cwd().resolve()


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ----------------------------
    # Application
    # ----------------------------
    APP_NAME: str = "Doitall"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ----------------------------
    # API
    # ----------------------------
    API_HOST: str = "127.0.0.1"
    API_PORT: int = Field(default=8000, gt=0, le=65535)
    API_KEY: str = ""
    METRICS_REQUIRE_API_KEY: bool = False

    # Allowed CORS origins. In development the default permits localhost
    # frontends. In production set this to your actual frontend origin(s),
    # e.g. CORS_ORIGINS=["https://app.example.com"].
    # NOTE: do NOT use ["*"] together with credentials — browsers will reject it.
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:5173",
        ]
    )

    # Seconds of inactivity before an in-memory chat session is evicted.
    SESSION_TTL_SECONDS: PositiveInt = 3600
    MAX_HISTORY_MESSAGES: PositiveInt = 50
    CHAT_MESSAGE_MAX_LENGTH: PositiveInt = 10000
    INGEST_CONTENT_MAX_LENGTH: PositiveInt = 100000
    RATE_LIMIT_ENABLED: bool = True
    CHAT_RATE_LIMIT_PER_MINUTE: PositiveInt = 60
    INGEST_RATE_LIMIT_PER_MINUTE: PositiveInt = 20
    FILESYSTEM_MAX_READ_BYTES: PositiveInt = 1_000_000
    FILESYSTEM_MAX_LIST_ENTRIES: PositiveInt = 500
    FILESYSTEM_DENY_PATTERNS: list[str] = Field(
        default=[
            ".env",
            ".env.*",
            "*.pem",
            "*.key",
            "id_rsa",
            "id_ed25519",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "logs/*",
            "storage/*",
        ]
    )

    # ----------------------------
    # Database
    # ----------------------------
    DATABASE_URL: str = Field(default="sqlite:///storage/doitall.db")

    # ----------------------------
    # Logging
    # ----------------------------
    LOG_LEVEL: str = "INFO"

    # ----------------------------
    # Security
    # ----------------------------
    ENABLE_FILESYSTEM_WRITE_TOOLS: bool = False

    # Skill capabilities allowed by the application.
    #
    # An empty list means no capability restriction is applied.
    # Add capabilities here to explicitly restrict which privileged
    # skills may execute.
    SKILL_ALLOWED_CAPABILITIES: list[str] = Field(default_factory=list)

    # ----------------------------
    # Memory
    # ----------------------------
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-large"

    # ----------------------------
    # AI Providers
    # ----------------------------
    DEFAULT_PROVIDER: str = "gemini"

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ----------------------------
    # Default Models
    # ----------------------------
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_MODEL: str = "gemini/gemini-2.5-flash"
    GROQ_MODEL: str = "groq/llama-3.3-70b-versatile"
    ANTHROPIC_MODEL: str = "anthropic/claude-3-5-sonnet-20241022"
    NVIDIA_MODEL: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    OLLAMA_MODEL: str = "ollama/llama3.2"
    OPENROUTER_MODEL: str = "openrouter/anthropic/claude-3.5-sonnet"

    # ----------------------------
    # LLM call timeout
    # ----------------------------
    LLM_TIMEOUT_SECONDS: PositiveInt = 30
    """Seconds before an LLM completion call is aborted. Set higher for slow models."""

    # ----------------------------
    # Tool execution timeout
    # ----------------------------
    TOOL_EXECUTION_TIMEOUT_SECONDS: PositiveInt = 30
    """Seconds before an individual tool execution is aborted."""

    MAX_CONCURRENT_TOOL_CALLS: PositiveInt = 5
    """Maximum number of tool calls that may execute concurrently."""

    MAX_TOOL_ITERATIONS: PositiveInt = 10
    """Maximum number of tool-calling iterations allowed for a single agent request."""

    MAX_TOOL_CALLS_PER_REQUEST: PositiveInt = 50
    """Maximum number of tool calls allowed during a single agent request."""

    MAX_IDENTICAL_TOOL_CALLS: PositiveInt = 3
    """Maximum number of identical tool calls allowed during a single agent request."""

    # ----------------------------
    # Paths
    # ----------------------------
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    STORAGE_DIR: Path = BASE_DIR / "storage"
    LOG_DIR: Path = BASE_DIR / "logs"

    @model_validator(mode="after")
    def derive_runtime_directories(self) -> Self:
        """Derive child paths from an overridden base unless set explicitly."""
        if "DATA_DIR" not in self.model_fields_set:
            object.__setattr__(self, "DATA_DIR", self.BASE_DIR / "data")
        if "STORAGE_DIR" not in self.model_fields_set:
            object.__setattr__(self, "STORAGE_DIR", self.BASE_DIR / "storage")
        if "LOG_DIR" not in self.model_fields_set:
            object.__setattr__(self, "LOG_DIR", self.BASE_DIR / "logs")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings to avoid repeated loading from disk/environment."""
    return Settings()


# Global singleton instance of application settings
settings = get_settings()
