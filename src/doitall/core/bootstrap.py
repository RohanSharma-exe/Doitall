from pathlib import Path

from loguru import logger

from doitall.config.logging import configure_logging
from doitall.config.settings import settings
from doitall.database.session import engine
from doitall.providers.manager import ProviderManager
from doitall.services.registry import container
from doitall.skills.builtin import register_builtin_skills
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry
from doitall.workspace.workspace import Workspace


def bootstrap() -> None:
    """Initialize the application."""

    configure_logging()

    provider_manager = ProviderManager()

    from doitall.providers.registry import register_providers

    register_providers(provider_manager)

    skill_registry = SkillRegistry()
    skill_manager = SkillManager(
        skill_registry,
        container,
    )

    register_builtin_skills(skill_registry)

    container.register("settings", settings)
    container.register("engine", engine)
    container.register("provider_manager", provider_manager)
    container.register("skill_registry", skill_registry)
    container.register("skill_manager", skill_manager)
    workspace = Workspace(Path.cwd())

    container.register("workspace", workspace)

    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
