"""Database migration utilities.

Importing this module registers all SQLModel table metadata so that
``SQLModel.metadata.create_all(engine)`` creates every table.
"""
# noqa: F401 — side-effect imports register table metadata
from sqlmodel import SQLModel

import doitall.database.models  # noqa: F401
from doitall.database.session import engine


def create_database() -> None:
    """Create all database tables (idempotent — safe to call on every startup)."""
    SQLModel.metadata.create_all(engine)
