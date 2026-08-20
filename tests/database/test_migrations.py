"""Focused smoke tests for database migrations."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Text, create_engine, inspect

from doitall.config.settings import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_upgrade_from_0001_to_head_adds_execution_metadata_column(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = tmp_path / "migration-smoke.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", database_url)

    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))

    command.upgrade(config, "0001_initial_sessions")

    engine = create_engine(database_url)
    assert "execution_metadata_json" not in {
        column["name"] for column in inspect(engine).get_columns("messages")
    }

    command.upgrade(config, "head")

    columns = {
        column["name"]: column for column in inspect(engine).get_columns("messages")
    }
    execution_metadata = columns["execution_metadata_json"]
    assert isinstance(execution_metadata["type"], Text)
    assert execution_metadata["nullable"] is True

    with engine.connect() as connection:
        revision = MigrationContext.configure(connection).get_current_revision()
    assert revision == "0003_message_history_index"
    indexes = {index["name"] for index in inspect(engine).get_indexes("messages")}
    assert "ix_messages_session_created_at" in indexes
    engine.dispose()
