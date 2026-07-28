from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings."""

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
    API_PORT: int = 8000

    # ----------------------------
    # Database
    # ----------------------------
    DATABASE_URL: str = Field(default="sqlite:///storage/doitall.db")

    # ----------------------------
    # Logging
    # ----------------------------
    LOG_LEVEL: str = "INFO"

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
    GEMINI_MODEL: str = "gemini/gemini-2.5-flash"
    GROQ_MODEL: str = "groq/llama-3.3-70b-versatile"
    NVIDIA_MODEL: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    OLLAMA_MODEL: str = "ollama/llama3.2"

    # ----------------------------
    # Paths
    # ----------------------------
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    STORAGE_DIR: Path = BASE_DIR / "storage"
    LOG_DIR: Path = BASE_DIR / "logs"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
