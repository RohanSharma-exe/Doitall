"""Loguru logging configuration module.

Sets up console and file sinks for application-wide logging based on settings.
"""

from pathlib import Path

from loguru import logger

from doitall.config.settings import settings


def configure_logging() -> None:
    """Configure Loguru logging sinks for stdout and file output.

    Removes default handlers and adds:
    1. A colorized stdout console sink configured at the specified log level.
    2. A rotating, queued file sink in the configured log directory.
    """

    # Remove standard default loguru handler
    logger.remove()

    # Add console sink writing to standard output
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # Ensure log directory exists before initializing file sink
    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)

    # Add file sink with rotation, retention, and diagnostic features
    logger.add(
        Path(settings.LOG_DIR) / "doitall.log",
        rotation="10 MB",
        retention=10,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

