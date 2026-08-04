"""Application constants and path definitions.

Defines global naming, versioning, directory layout, default encoding,
and supported LLM provider keys used throughout the application.
"""

from pathlib import Path

# General application metadata
APP_NAME = "Doitall"
APP_VERSION = "0.1.0"

# Core project directory resolution based on file location
ROOT_DIR = Path(__file__).resolve().parents[3]

# Subdirectory paths relative to project root
SRC_DIR = ROOT_DIR / "src"
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
STORAGE_DIR = ROOT_DIR / "storage"
TMP_DIR = ROOT_DIR / "tmp"

# Default character encoding for text file operations
DEFAULT_ENCODING = "utf-8"

# Tuple of supported LLM provider identifiers
SUPPORTED_LLM_PROVIDERS = (
    "openai",
    "anthropic",
    "google",
    "groq",
    "ollama",
    "openrouter",
)

# Default provider used when none is explicitly specified
DEFAULT_PROVIDER = "gemini"

