from sqlmodel import Session, create_engine

from doitall.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


def get_session() -> Session:
    """Return a database session."""
    return Session(engine)
