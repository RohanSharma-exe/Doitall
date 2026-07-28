from pathlib import Path

APP_NAME = "Doitall"
APP_VERSION = "0.1.0"

ROOT_DIR = Path(__file__).resolve().parents[3]

SRC_DIR = ROOT_DIR / "src"
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
STORAGE_DIR = ROOT_DIR / "storage"
TMP_DIR = ROOT_DIR / "tmp"

DEFAULT_ENCODING = "utf-8"

SUPPORTED_LLM_PROVIDERS = (
    "openai",
    "anthropic",
    "google",
    "groq",
    "ollama",
    "openrouter",
)

DEFAULT_PROVIDER = "openai"
