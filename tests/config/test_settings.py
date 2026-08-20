from pathlib import Path

import pytest
from pydantic import ValidationError

from doitall.config.settings import Settings

POSITIVE_OPERATIONAL_SETTINGS = (
    "API_PORT",
    "SESSION_TTL_SECONDS",
    "MAX_HISTORY_MESSAGES",
    "CHAT_MESSAGE_MAX_LENGTH",
    "INGEST_CONTENT_MAX_LENGTH",
    "CHAT_RATE_LIMIT_PER_MINUTE",
    "INGEST_RATE_LIMIT_PER_MINUTE",
    "FILESYSTEM_MAX_READ_BYTES",
    "FILESYSTEM_MAX_LIST_ENTRIES",
    "LLM_TIMEOUT_SECONDS",
    "TOOL_EXECUTION_TIMEOUT_SECONDS",
    "MAX_CONCURRENT_TOOL_CALLS",
    "MAX_TOOL_ITERATIONS",
    "MAX_TOOL_CALLS_PER_REQUEST",
    "MAX_IDENTICAL_TOOL_CALLS",
)


@pytest.mark.parametrize("setting_name", POSITIVE_OPERATIONAL_SETTINGS)
@pytest.mark.parametrize("invalid_value", [0, -1])
def test_operational_settings_must_be_positive(
    setting_name: str, invalid_value: int
) -> None:
    with pytest.raises(ValidationError):
        _ = Settings.model_validate({setting_name: invalid_value})


def test_api_port_must_be_in_valid_range() -> None:
    with pytest.raises(ValidationError):
        _ = Settings.model_validate({"API_PORT": 65536})


def test_runtime_directories_follow_overridden_base(tmp_path: Path) -> None:
    configured = Settings.model_validate({"BASE_DIR": tmp_path})

    assert tmp_path / "data" == configured.DATA_DIR
    assert tmp_path / "storage" == configured.STORAGE_DIR
    assert tmp_path / "logs" == configured.LOG_DIR


def test_explicit_runtime_directory_is_preserved(tmp_path: Path) -> None:
    explicit_data = tmp_path / "custom-data"
    configured = Settings.model_validate(
        {"BASE_DIR": tmp_path, "DATA_DIR": explicit_data}
    )

    assert explicit_data == configured.DATA_DIR
