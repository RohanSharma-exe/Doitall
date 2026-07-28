from sqlmodel import SQLModel

from doitall.database.session import engine


def create_database() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
