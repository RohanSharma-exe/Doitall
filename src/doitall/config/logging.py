from pathlib import Path

from loguru import logger

from doitall.config.settings import settings


def configure_logging() -> None:
    """Configure Loguru for the application."""

    logger.remove()

    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)

    logger.add(
        Path(settings.LOG_DIR) / "doitall.log",
        rotation="10 MB",
        retention=10,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
