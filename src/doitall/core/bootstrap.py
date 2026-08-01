from loguru import logger
from qdrant_client import AsyncQdrantClient

import doitall.database.models  # noqa: F401 — registers SQLModel table metadata
from doitall.config.logging import configure_logging
from doitall.config.settings import settings
from doitall.database.session import engine, init_db
from doitall.database.session_repository import SessionRepository
from doitall.embeddings.manager import EmbeddingManager
from doitall.knowledge.ingestion import KnowledgeIngestionService
from doitall.knowledge.simple_chunker import SimpleChunker
from doitall.knowledge.vector_repository import VectorKnowledgeRepository
from doitall.memory.constants import get_vector_size_for_model
from doitall.memory.qdrant_repository import QdrantRepository
from doitall.memory.qdrant_store import QdrantStore
from doitall.memory.vector_memory_store import VectorMemoryStore
from doitall.providers.manager import ProviderManager
from doitall.services.registry import container
from doitall.skills.builtin import register_builtin_skills
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry
from doitall.workspace.workspace import Workspace

_bootstrap_has_run = False


def bootstrap() -> None:
    """Synchronous bootstrap — wires all services into the DI container.

    This must be called before the first request is handled.  It does NOT
    perform any async I/O.  Async initialisation (Qdrant collection creation)
    is handled by ``async_bootstrap()``, which the FastAPI lifespan awaits
    immediately after calling this function.
    """

    global _bootstrap_has_run

    if _bootstrap_has_run:
        logger.warning(
            "Bootstrap has already been called. Skipping duplicate initialization."
        )
        return

    _bootstrap_has_run = True

    configure_logging()

    if settings.ENVIRONMENT == "production" and settings.DEBUG:
        raise RuntimeError("Refusing to start production with DEBUG=True")
    if settings.ENVIRONMENT == "production" and "*" in settings.CORS_ORIGINS:
        raise RuntimeError("Refusing to start production with wildcard CORS origins")
    if settings.ENVIRONMENT == "production" and not settings.API_KEY:
        raise RuntimeError("Refusing to start production without API_KEY")

    # Initialize database
    init_db()

    provider_manager = ProviderManager()

    embedding_manager = EmbeddingManager.from_model(
        settings.EMBEDDING_MODEL,
    )

    # Build async Qdrant client — all I/O goes through the event loop.
    qdrant_client = AsyncQdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )

    # Memory store — uses the 'memories' collection
    qdrant_store = QdrantStore(
        client=qdrant_client,
        collection_name="memories",
        vector_size=get_vector_size_for_model(settings.EMBEDDING_MODEL),
    )

    # Knowledge store — uses a SEPARATE 'knowledge' collection to prevent
    # payload key collisions when searching (memory and chunk payloads differ)
    knowledge_qdrant_store = QdrantStore(
        client=qdrant_client,
        collection_name="knowledge",
        vector_size=get_vector_size_for_model(settings.EMBEDDING_MODEL),
    )

    qdrant_repository = QdrantRepository(
        vector_store=qdrant_store,
        embedding_manager=embedding_manager,
    )

    memory_store = VectorMemoryStore(
        repository=qdrant_repository,
    )

    knowledge_repository = VectorKnowledgeRepository(
        chunker=SimpleChunker(),
        embedding_manager=embedding_manager,
        vector_store=knowledge_qdrant_store,
    )

    knowledge_ingestion = KnowledgeIngestionService(
        repository=knowledge_repository,
    )

    from doitall.providers.registry import register_providers

    register_providers(provider_manager)

    # Only set default if it was actually registered (key might be missing).
    if provider_manager.exists(settings.DEFAULT_PROVIDER):
        provider_manager.set_default(settings.DEFAULT_PROVIDER)
    elif provider_manager.names():
        logger.warning(
            f"Configured DEFAULT_PROVIDER='{settings.DEFAULT_PROVIDER}' was not registered "
            f"(no API key?). Using first available: '{provider_manager.names()[0]}'."
        )

    skill_registry = SkillRegistry()
    skill_manager = SkillManager(
        skill_registry,
        container,
    )

    register_builtin_skills(skill_registry)

    workspace = Workspace(settings.BASE_DIR)

    # --- Register all services in the DI container ---
    container.register("settings", settings)
    container.register("engine", engine)
    container.register("provider_manager", provider_manager)
    container.register("embedding_manager", embedding_manager)
    container.register("qdrant_client", qdrant_client)
    container.register("qdrant_store", qdrant_store)
    container.register("knowledge_qdrant_store", knowledge_qdrant_store)
    container.register("qdrant_repository", qdrant_repository)
    container.register("memory_store", memory_store)
    container.register("knowledge_repository", knowledge_repository)
    container.register("knowledge_ingestion", knowledge_ingestion)
    container.register("skill_registry", skill_registry)
    container.register("skill_manager", skill_manager)
    container.register("workspace", workspace)
    container.register("session_repository", SessionRepository())

    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")


async def async_bootstrap() -> None:
    """Async initialisation — must be awaited inside the running event loop.

    Creates Qdrant collections if they do not already exist.  Call this from
    the FastAPI lifespan *after* ``bootstrap()`` has returned.
    """
    qdrant_store: QdrantStore = container.resolve("qdrant_store")
    knowledge_qdrant_store: QdrantStore = container.resolve("knowledge_qdrant_store")

    await qdrant_store.ensure_collection()
    await knowledge_qdrant_store.ensure_collection()
    logger.info("Qdrant collections ready.")


def cleanup() -> None:
    """Clean up resources when shutting down the application."""

    global _bootstrap_has_run

    if not _bootstrap_has_run:
        return

    logger.info("Cleaning up resources...")

    try:
        # Close async Qdrant client
        if container.has("qdrant_client"):
            qdrant_client: AsyncQdrantClient = container.resolve("qdrant_client")
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(qdrant_client.close())
                else:
                    loop.run_until_complete(qdrant_client.close())
                logger.info("Qdrant client closed")
            except Exception as e:
                logger.warning(f"Failed to close Qdrant client: {e}")

        # Dispose database engine
        if container.has("engine"):
            db_engine = container.resolve("engine")
            try:
                db_engine.dispose()
                logger.info("Database engine disposed")
            except Exception as e:
                logger.warning(f"Failed to dispose database engine: {e}")

        # Clear the container
        container.clear()

        logger.info("Cleanup completed")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    finally:
        _bootstrap_has_run = False
