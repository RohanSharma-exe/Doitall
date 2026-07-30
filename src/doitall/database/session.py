"""Database session management."""

from sqlmodel import SQLModel, create_engine

from doitall.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


def init_db() -> None:
    """Initialize the database by creating all tables.

    This function should be called during application startup to ensure
    all database tables are created based on the defined SQLModel classes.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """Return a database session.

    Returns:
        A new SQLAlchemy Session instance for database operations.
    """
    from sqlmodel import Session

    return Session(engine)
