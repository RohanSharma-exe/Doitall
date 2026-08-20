# Doitall Bug Tracker

Updated: 2026-08-14

Status legend: `TODO`, `IN PROGRESS`, `DONE`, `BLOCKED`, `DEFERRED`

## P0 — Release blockers

| ID | Status | Resolution | Validation |
|---|---|---|---|
| BUG-001 | DONE | Added migrations `0002` for `messages.execution_metadata_json` and `0003` for the history index | Alembic upgrade smoke test and metadata round-trip test pass |
| BUG-002 | DONE | Streaming failover stops after output begins; no provider responses can be concatenated | Runtime partial-stream failure regressions pass |
| BUG-003 | DONE | Added a per-hot-session async turn lock around complete normal and streaming turns | Concurrent same-session regression proves maximum concurrency is one |
| BUG-021 | DONE | Fixed Docker build order so dependencies sync before the project source is installed | Production image builds successfully |
| BUG-022 | DONE | Removed `uv run` from the non-root container runtime, avoiding `/nonexistent/.cache/uv` failure | Non-root container imports `doitall.api.app` successfully |

## P1 — High priority

| ID | Status | Resolution | Validation |
|---|---|---|---|
| BUG-004 | DONE | Unverified credential values use the client IP bucket; valid credentials map to a stable principal label; raw secrets are never retained | Fake-header rotation and secret-retention tests pass |
| BUG-005 | DONE | Explicit providers are pinned, unknown providers raise, and only classified transient errors fail over | Provider manager and runtime failover regressions pass |
| BUG-006 | DONE | Lifespan startup/yield is wrapped in `try/finally`; partial async bootstrap failure triggers cleanup | Bootstrap-failure cleanup test passes |
| BUG-007 | DONE | Every SSE response emits the session event before command/model output | Normal and command streaming API tests pass |
| BUG-008 | DONE | Slash-command user/assistant messages and session rows are persisted before returning the session ID | Returned command session exists with two messages in regression test |
| BUG-009 | DONE | Chat persistence/hydration and readiness SQL probes run through `asyncio.to_thread`; synchronous FastAPI session endpoints remain thread-pooled | Chat, context, health, and concurrency suites pass |
| BUG-010 | DONE | Compose waits for healthy Qdrant and restarts the API on failure | Deployment config tests and `docker compose config --quiet` pass |

## P2 — Important

| ID | Status | Resolution | Validation |
|---|---|---|---|
| BUG-011 | DONE | Added positive/range constraints to operational limits, ports, concurrency, and timeouts | 33 settings boundary tests pass |
| BUG-012 | DONE | Added direct session lookup, SQL/grouped counts, bounded API pagination, and `(session_id, created_at)` index | Repository, API pagination, and migration tests pass |
| BUG-013 | DONE | Explicitly documented the supported trusted single-tenant boundary and requirements before multi-tenant use | README and production checklist updated |
| BUG-014 | DONE | Metadata now has serialized-byte, nesting-depth, key-length, key-count, JSON-type, and finite-number limits | Metadata validation tests pass |
| BUG-015 | DONE | Chunk IDs are deterministic, embeddings are batched, and all Qdrant points are submitted in one batch request | Batch failure/retry and deterministic-ID tests pass |
| BUG-016 | DONE | Public readiness uses stable sanitized details while full exceptions remain in server logs | Health route regressions pass |
| BUG-017 | DONE | Documented process-local metrics/rate behavior and constrained supported deployment to one process until shared backends are configured | README and production checklist updated |
| BUG-018 | DONE | Runtime paths derive from launch/configured `BASE_DIR`, preserve explicit overrides, and Docker sets absolute persistent paths | Path tests, wheel build, Compose config, and container import pass |

## P3 — Quality

| ID | Status | Resolution | Validation |
|---|---|---|---|
| BUG-019 | DONE | Applied Ruff fixes and formatting across the tree | Ruff check and format check pass for 254 files |
| BUG-020 | DONE | Added regressions for migrations, failover, partial streams, provider pinning, concurrency, limiter identity, cleanup, SSE sessions, command persistence, settings, metadata, ingestion, health, deployment, pagination, paths, and packaging | Full suite passes: 380 tests |

## Final validation

- `pytest -q`: **380 passed**
- `ruff check`: **passed**
- `ruff format --check`: **254 files formatted**
- `mypy src --no-incremental`: **passed, 145 source files**
- `docker compose config --quiet`: **passed**
- `uv build`: **source distribution and wheel built successfully**
- `docker build -t doitall-audit:latest doitall`: **passed**
- Container import smoke test: **passed** (`container-import-ok`)

## Work log

- 2026-08-14: Tracker created from `AUDIT_REPORT.md`.
- 2026-08-14: Completed P0 migration, streaming failover, and session concurrency fixes.
- 2026-08-14: Completed P1 authentication/rate-limit, provider, lifecycle, streaming, command persistence, async DB boundary, and Compose fixes.
- 2026-08-14: Completed P2 settings, query, metadata, ingestion, health, deployment-boundary, and runtime-path fixes.
- 2026-08-14: Restored all quality gates and expanded the suite from 319 to 380 tests.
- 2026-08-14: Real Docker validation discovered and resolved BUG-021 and BUG-022.
