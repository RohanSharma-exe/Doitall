"""Database session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from doitall.config.settings import settings

# Only echo SQL in development — never in production where it leaks query
# details and creates significant log noise.
_sql_echo = settings.DEBUG and settings.ENVIRONMENT != "production"

engine = create_engine(
    settings.DATABASE_URL,
    echo=_sql_echo,
)


def init_db() -> None:
    """Initialize the database by creating all tables.

    This function should be called during application startup to ensure
    all database tables are created based on the defined SQLModel classes.
    """
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session]:
    """Context-manager that yields a database session and guarantees close.

    Usage::

        with get_session() as session:
            session.add(obj)
            session.commit()
    """
    with Session(engine) as session:
        yield session
