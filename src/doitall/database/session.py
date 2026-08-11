"""Database session management."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine

from doitall.config.settings import settings

# Only echo SQL in development — never in production where it leaks query
# details and creates significant log noise.
_sql_echo = settings.DEBUG and settings.ENVIRONMENT != "production"


def _prepare_sqlite_database_path(database_url: str) -> None:
    """Create the parent directory for a file-based SQLite database.

    SQLite creates the database file itself, but it does not create missing
    parent directories. This helper therefore prepares the filesystem only
    when the configured database URL points to a SQLite file.

    Server-backed databases such as PostgreSQL do not require filesystem
    preparation and are intentionally left untouched.
    """
    url = make_url(database_url)

    if url.get_backend_name() != "sqlite":
        return

    database = url.database

    # SQLite in-memory databases do not have a filesystem path.
    if not database or database == ":memory:":
        return

    database_path = Path(database)

    if not database_path.is_absolute():
        database_path = Path.cwd() / database_path

    database_path.parent.mkdir(parents=True, exist_ok=True)


_prepare_sqlite_database_path(settings.DATABASE_URL)

engine = create_engine(
    settings.DATABASE_URL,
    echo=_sql_echo,
)


def init_db() -> None:
    """Initialize the database by creating all tables from SQLModel metadata.

    Schema strategy:
    ``create_all()`` is the primary mechanism for table creation in both
    development and fresh production deployments. Alembic migrations
    (``migrations/``) exist as a forward-looking tool for applying
    column-level changes to existing tables, but they are not run
    automatically at startup.

    When a migration is needed, run ``alembic upgrade head`` as an explicit
    operations step before starting the API.

    If you add or rename a column on a table that already exists in a live
    database, you must create an Alembic migration for it because
    ``create_all()`` will not alter existing tables.
    """
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session]:
    """Yield a database session and guarantee that it is closed.

    Usage::

        with get_session() as session:
            session.add(obj)
            session.commit()
    """
    with Session(engine) as session:
        yield session
