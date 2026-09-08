"""Tests for ToolCallingEngine — now wired directly to SkillManager."""

import asyncio

import pytest

from doitall.models.provider_response import ProviderResponse
from doitall.models.tool_call import ToolCall
from doitall.services.container import ServiceContainer
from doitall.services.tool_calling_engine import ToolCallingEngine
from doitall.skills.calculator import CalculatorSkill
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


def _make_engine() -> tuple[ToolCallingEngine, SkillManager]:
    registry = SkillRegistry()
    registry.register(CalculatorSkill)
    manager = SkillManager(registry, ServiceContainer())
    return ToolCallingEngine(manager), manager


@pytest.mark.asyncio
async def test_execute_tool_calls():
    engine, _ = _make_engine()

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="1",
                name="calculator",
                arguments={
                    "expression": "2+3",
                },
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].tool_call_id == "1"
    assert results[0].result == 5


@pytest.mark.asyncio
async def test_execute_multiple_tool_calls():
    engine, _ = _make_engine()

    response = ProviderResponse(
        tool_calls=[
            ToolCall(
                id="1",
                name="calculator",
                arguments={"expression": "2+2"},
            ),
            ToolCall(
                id="2",
                name="calculator",
                arguments={"expression": "10*5"},
            ),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2
    assert results[0].result == 4
    assert results[1].result == 50


@pytest.mark.asyncio
async def test_execute_tool_calls_continues_after_failure() -> None:
    engine, _ = _make_engine()

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="failed", name="unknown_skill", arguments={}),
            ToolCall(id="successful", name="calculator", arguments={"expression": "10*5"}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2
    assert results[0].tool_call_id == "failed"
    assert results[0].name == "unknown_skill"
    assert isinstance(results[0].result, str)
    assert results[0].result.startswith("Tool execution failed:")

    assert results[1].tool_call_id == "successful"
    assert results[1].name == "calculator"
    assert results[1].result == 50


@pytest.mark.asyncio
async def test_invalid_tool_arguments_do_not_prevent_remaining_tools() -> None:
    engine, _ = _make_engine()

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="invalid", name="calculator", arguments={"expression": 123}),
            ToolCall(id="valid", name="calculator", arguments={"expression": "10*5"}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2
    assert results[0].tool_call_id == "invalid"
    assert results[0].name == "calculator"
    assert isinstance(results[0].result, str)
    assert results[0].result.startswith("Tool execution failed:")
    assert results[0].metadata is not None
    assert results[0].metadata.status == "error"

    assert results[1].tool_call_id == "valid"
    assert results[1].name == "calculator"
    assert results[1].result == 50
    assert results[1].metadata is not None
    assert results[1].metadata.status == "success"


@pytest.mark.asyncio
async def test_execute_tool_call_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    engine, skill_manager = _make_engine()

    async def slow_execute(name: str, **kwargs: object) -> object:
        await asyncio.sleep(1)
        return "should not complete"

    monkeypatch.setattr(skill_manager, "execute", slow_execute)
    monkeypatch.setattr(
        "doitall.services.tool_calling_engine.settings.TOOL_EXECUTION_TIMEOUT_SECONDS",
        0.01,
    )

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="timeout", name="slow_tool", arguments={}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].tool_call_id == "timeout"
    assert results[0].name == "slow_tool"
    assert results[0].result == "Tool execution timed out after 0.01 seconds."


@pytest.mark.asyncio
async def test_timeout_does_not_prevent_remaining_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, skill_manager = _make_engine()

    monkeypatch.setattr(
        "doitall.services.tool_calling_engine.settings.TOOL_EXECUTION_TIMEOUT_SECONDS",
        0.01,
    )

    original_execute = skill_manager.execute

    async def execute_with_one_timeout(name: str, **kwargs: object) -> object:
        if name == "slow_tool":
            await asyncio.sleep(1)
        return await original_execute(name, **kwargs)

    monkeypatch.setattr(skill_manager, "execute", execute_with_one_timeout)

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="timeout", name="slow_tool", arguments={}),
            ToolCall(id="successful", name="calculator", arguments={"expression": "10*5"}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 2
    assert results[0].tool_call_id == "timeout"
    assert results[0].result.startswith("Tool execution timed out")

    assert results[1].tool_call_id == "successful"
    assert results[1].result == 50


@pytest.mark.asyncio
async def test_execute_tool_calls_concurrently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, skill_manager = _make_engine()

    active_calls = 0
    max_active_calls = 0
    original_execute = skill_manager.execute

    async def tracked_execute(name: str, **kwargs: object) -> object:
        nonlocal active_calls, max_active_calls
        active_calls += 1
        max_active_calls = max(max_active_calls, active_calls)
        try:
            await asyncio.sleep(0.05)
            return await original_execute(name, **kwargs)
        finally:
            active_calls -= 1

    monkeypatch.setattr(skill_manager, "execute", tracked_execute)

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="1", name="calculator", arguments={"expression": "2+3"}),
            ToolCall(id="2", name="calculator", arguments={"expression": "10*5"}),
            ToolCall(id="3", name="calculator", arguments={"expression": "7*6"}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 3
    assert max_active_calls == 3
    assert results[0].result == 5
    assert results[1].result == 50
    assert results[2].result == 42


@pytest.mark.asyncio
async def test_execute_tool_calls_respects_concurrency_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, skill_manager = _make_engine()

    monkeypatch.setattr(
        "doitall.services.tool_calling_engine.settings.MAX_CONCURRENT_TOOL_CALLS",
        2,
    )

    active_calls = 0
    max_active_calls = 0
    original_execute = skill_manager.execute

    async def tracked_execute(name: str, **kwargs: object) -> object:
        nonlocal active_calls, max_active_calls
        active_calls += 1
        max_active_calls = max(max_active_calls, active_calls)
        try:
            await asyncio.sleep(0.05)
            return await original_execute(name, **kwargs)
        finally:
            active_calls -= 1

    monkeypatch.setattr(skill_manager, "execute", tracked_execute)

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="1", name="calculator", arguments={"expression": "2+3"}),
            ToolCall(id="2", name="calculator", arguments={"expression": "10*5"}),
            ToolCall(id="3", name="calculator", arguments={"expression": "7*6"}),
            ToolCall(id="4", name="calculator", arguments={"expression": "8*8"}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 4
    assert max_active_calls == 2
    assert results[0].result == 5
    assert results[1].result == 50
    assert results[2].result == 42
    assert results[3].result == 64


@pytest.mark.asyncio
async def test_successful_tool_execution_includes_metadata() -> None:
    engine, _ = _make_engine()

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="1", name="calculator", arguments={"expression": "2+3"}),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].result == 5
    assert results[0].metadata is not None
    assert results[0].metadata.status == "success"
    assert results[0].metadata.duration_ms >= 0
    assert results[0].metadata.duration_ms < 1000
    assert results[0].metadata.error is None


@pytest.mark.asyncio
async def test_timeout_includes_timeout_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "doitall.services.tool_calling_engine.settings.TOOL_EXECUTION_TIMEOUT_SECONDS",
        0.01,
    )

    class SlowSkillManager:
        async def execute(self, name: str, **kwargs: object) -> object:
            await asyncio.sleep(1)
            return "done"

    engine = ToolCallingEngine(SlowSkillManager())  # type: ignore[arg-type]

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="timeout-1", name="slow"),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].metadata is not None
    assert results[0].metadata.status == "timeout"
    assert results[0].metadata.duration_ms >= 0
    assert results[0].metadata.error == "timeout"


@pytest.mark.asyncio
async def test_failed_tool_execution_includes_error_metadata() -> None:
    class FailingSkillManager:
        async def execute(self, name: str, **kwargs: object) -> object:
            raise RuntimeError("boom")

    engine = ToolCallingEngine(FailingSkillManager())  # type: ignore[arg-type]

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="error-1", name="failing_tool"),
        ],
    )

    results = await engine.execute(response)

    assert len(results) == 1
    assert results[0].metadata is not None
    assert results[0].metadata.status == "error"
    assert results[0].metadata.duration_ms >= 0
    assert results[0].metadata.error == "boom"


@pytest.mark.asyncio
async def test_request_cancellation_propagates() -> None:
    started = asyncio.Event()
    cancelled = asyncio.Event()

    class SlowSkillManager:
        async def execute(self, name: str, **kwargs: object) -> object:
            started.set()
            try:
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                cancelled.set()
                raise
            return "should not complete"

    engine = ToolCallingEngine(SlowSkillManager())  # type: ignore[arg-type]

    response = ProviderResponse(
        tool_calls=[
            ToolCall(id="cancel-1", name="slow", arguments={}),
        ],
    )

    task = asyncio.create_task(engine.execute(response))

    await asyncio.wait_for(started.wait(), timeout=1)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert cancelled.is_set()
