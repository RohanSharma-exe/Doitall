# Doitall Code Audit Report

**Audit date:** 2026-08-14  
**Scope:** application code, API behavior, persistence, provider failover, security controls, deployment configuration, migrations, and automated quality gates.

## Executive summary

The codebase has good structure and broad unit coverage: all **319 tests pass**, and mypy reports no issues across **145 source files**. However, several production-path defects are not covered by the tests. The highest-risk problems are schema drift in the Alembic migration, response corruption during streaming failover, concurrent requests corrupting session ordering, and a bypassable rate limiter.

Fix the migration and streaming/session correctness issues before adding features or optimizing performance.

## Validation performed

| Check | Result |
|---|---|
| `pytest -q` | **Passed:** 319 tests in 21.82s |
| `mypy src --no-incremental` | **Passed:** no issues in 145 source files |
| `ruff check .` | **Failed:** 4 fixable violations |
| `ruff format --check .` | **Failed:** 5 files need formatting |
| Editor diagnostics | **Passed:** no errors or warnings |
| Docker build | Not run; Docker is installed, but a build may require network access |

Because CI runs Ruff before pytest, the current `.github/workflows/ci.yml` pipeline is expected to fail even though all tests pass.

---

# Prioritized findings

## P0 — Fix before production use

### 1. Alembic-created databases are missing a required column

**Evidence**

- `src/doitall/database/models.py:60` defines `MessageRecord.execution_metadata_json`.
- `migrations/versions/0001_initial_sessions.py:28-40` creates `messages` without that column.
- `src/doitall/database/session_repository.py:158-159` writes the missing field for tool messages.

**Impact**

A fresh database made by `SQLModel.metadata.create_all()` works, but a database created or upgraded with `alembic upgrade head` lacks the column. Persisting or loading tool execution metadata can then fail with an SQL “no such column” error. This is especially dangerous because development and production can behave differently.

**Fix steps**

1. Add a new Alembic revision; do not edit an already-applied migration.
2. Add nullable `messages.execution_metadata_json` as `Text`.
3. Run `alembic upgrade head` against an empty database and an existing revision-0001 database.
4. Add a migration smoke test that inserts and reloads a `ToolMessage` through `SessionRepository`.
5. Make migration execution the documented deployment path; avoid relying on `create_all()` to evolve schemas.

### 2. Streaming failover can combine two providers into one corrupted answer

**Evidence**

`src/doitall/runtime/executor.py:90-150` yields chunks immediately. If a provider emits some chunks and then raises, the loop continues to another provider and yields that provider’s full response into the same stream. The retry-without-tools path at lines 112-137 has the same problem.

**Impact**

A client may receive:

```text
<partial answer from provider A><complete answer from provider B>
```

The combined output can be contradictory, malformed, or unsafe. It may also cause the persisted assistant response to differ from what any single provider generated.

**Fix steps**

1. Decide the contract: either fail the stream after the first emitted chunk, or buffer a candidate until it completes before exposing it.
2. Permit provider failover only before any bytes have been sent.
3. Never retry without tools after a provider has emitted content.
4. Add tests for failure before the first chunk and failure after one or more chunks.
5. Include provider/model identity in stream metadata so clients know which backend succeeded.

### 3. Concurrent requests to one session can interleave conversation state

**Evidence**

- `src/doitall/api/routes/chat.py:117-136` locks only cache lookup and returns a shared `ChatService`.
- `src/doitall/services/chat_service.py:39-68` and lines 92-141 mutate the shared conversation across multiple awaits.
- There is no per-session async lock around a complete chat turn.

**Impact**

Two requests using the same `session_id` can both append user messages, assemble overlapping contexts, execute providers, and append assistant/tool messages in the wrong order. The database history and in-memory history can diverge semantically even if individual inserts succeed.

**Fix steps**

1. Add an `asyncio.Lock` per hot session.
2. Hold it across the whole turn: user append, context assembly, tool loop, assistant append, and memory processing policy.
3. Define how a streaming request owns the session until completion or disconnect.
4. Clean up lock objects when hot sessions are evicted.
5. Add a test that starts two requests concurrently against one session and verifies deterministic message ordering.

---

## P1 — High priority

### 4. Rate limiting is bypassable and stores raw credentials in memory

**Evidence**

`src/doitall/api/app.py:50-57` uses any `X-API-Key` or `Authorization` value as the rate-limit identity before authentication runs. The raw value is embedded in `_rate_buckets` keys.

**Impact**

An unauthenticated caller can rotate fake header values to get a new bucket for every request. Valid API keys and bearer values are retained in process memory as dictionary keys. In a multi-worker deployment, each process also enforces an independent limit.

**Fix steps**

1. Do not trust unvalidated credential headers as identity.
2. Use client IP for unauthenticated requests and a non-reversible digest or stable principal ID after successful authentication.
3. Ensure proxy headers are trusted only from configured reverse proxies.
4. Move limits to a shared backend such as Redis when using multiple workers/replicas.
5. Add tests that rotate invalid API keys and verify they cannot bypass the limit.

### 5. Unknown or explicitly selected providers silently fall back

**Evidence**

- `src/doitall/providers/manager.py:68-88` ignores an unknown `preferred` name and returns all registered providers.
- `src/doitall/api/routes/chat.py:181-185` expects a `KeyError` for unknown providers, but this path does not raise one.
- `src/doitall/runtime/executor.py:170-234` catches every exception and tries another provider, including likely authentication, invalid-request, and policy errors.

**Impact**

A typo such as `provider="opneai"` can succeed through another provider instead of returning 422. Explicit provider selection may route data to an unrequested vendor, creating correctness, cost, privacy, and compliance risks.

**Fix steps**

1. Validate `request.provider` against `ProviderManager.exists()` before creating a session or calling a provider.
2. Define retryable exceptions explicitly (for example timeout, rate limit, and transient unavailability).
3. Do not fail over authentication, invalid request, unsupported model, or policy errors.
4. Decide whether explicit provider selection disables cross-provider failover by default.
5. Return the actual provider and model used in normal and streaming responses.
6. Add API and executor tests for unknown providers and non-retryable failures.

### 6. Lifespan cleanup is not guaranteed

**Evidence**

`src/doitall/api/app.py:107-115` runs cleanup only after `yield`, without `try/finally`.

**Impact**

If the application lifespan exits through an exception or cancellation, Qdrant and database resources may not be closed and the global container/bootstrap flag may remain dirty. This also makes repeated app startup in the same process unreliable.

**Fix steps**

1. Wrap `yield` in `try/finally` and call `await cleanup()` in `finally`.
2. If `async_bootstrap()` fails after synchronous bootstrap, clean up partially initialized resources before re-raising.
3. Add tests for normal shutdown, application failure after startup, and async bootstrap failure.

### 7. Normal SSE streams omit the documented session event

**Evidence**

- `README.md:258` says streams emit session metadata.
- `src/doitall/api/routes/chat.py:222-227` emits `event="session"` only for slash commands.
- The normal stream begins directly with token events at lines 244-252.

**Impact**

Clients that omit `session_id` do not learn the generated ID during a normal stream and cannot reliably continue the conversation.

**Fix steps**

1. Emit the session event before command execution or model work for every stream.
2. Include actual provider/model when known.
3. Add an API test for a normal stream with no incoming session ID.

### 8. Slash commands return “phantom” session IDs

**Evidence**

- `src/doitall/api/routes/chat.py:164-172` returns a generated session ID for commands without calling `_get_chat_service()` or creating a session row.
- The streaming equivalent returns early at lines 217-243.
- `tests/api/test_sessions_endpoints.py:210-237` explicitly asserts that command streams do not create a chat service, but does not verify the returned session exists.

**Impact**

Clients receive a session ID, but `GET /v1/sessions/{id}` returns 404 and command history is not persisted. The API contract is misleading.

**Fix steps**

1. Choose one contract: persist command sessions/messages, or return `session_id=null` for stateless commands.
2. Apply the same behavior to regular and streaming endpoints.
3. Add endpoint tests that follow the returned ID through the session API.

### 9. Synchronous database I/O blocks async routes

**Evidence**

- Async chat handlers call synchronous repository methods in `src/doitall/api/routes/chat.py:174-180` via `ChatService` and `ConversationService`.
- `src/doitall/api/routes/health.py:41-43` performs synchronous SQL inside an async readiness route.
- Session hydration and every message insert open synchronous SQLModel sessions.

**Impact**

Slow database operations block the event loop, delaying unrelated streaming and health requests. SQLite may hide this in tests, but network databases make it more visible.

**Fix steps**

1. Short term: move bounded synchronous DB operations to `asyncio.to_thread()`.
2. Preferred: introduce SQLAlchemy async sessions/repositories for async request paths.
3. Avoid holding the current thread lock during database work.
4. Add a concurrency test proving a slow database query does not stall liveness or an unrelated stream.

### 10. Startup is tightly coupled to Qdrant readiness

**Evidence**

- `src/doitall/core/bootstrap.py:167-178` requires both Qdrant collections during startup.
- `docker-compose.yml:23-25` waits only for `service_started`, not for a Qdrant health check.
- No restart policy is configured.

**Impact**

The API can exit during a normal Compose startup race even though Qdrant becomes ready shortly afterward. The liveness/readiness split is less useful if the process never starts when an optional/degraded dependency is unavailable.

**Fix steps**

1. Add a Qdrant health check and use `condition: service_healthy`, or add bounded startup retries with backoff.
2. Add an appropriate restart policy.
3. Decide whether chat without memory/RAG should run in degraded mode when Qdrant is unavailable.
4. Test delayed Qdrant startup in an integration environment.

---

## P2 — Important improvements

### 11. Configuration accepts invalid zero and negative limits

**Evidence**

`src/doitall/config/settings.py` declares timeouts, TTLs, rate limits, tool iteration limits, and concurrency limits as unconstrained integers.

**Impact**

Examples:

- `MAX_CONCURRENT_TOOL_CALLS=0` creates `Semaphore(0)`; calls wait forever before entering the code-level timeout.
- A zero rate limit rejects every request.
- Negative semaphore values fail at runtime.
- Invalid TTL/history values cause surprising behavior.

**Fix steps**

1. Add Pydantic constraints (`gt=0` or `ge=0`, as appropriate) to every numeric operational setting.
2. Validate `ENVIRONMENT`, URLs, log level, and provider names.
3. Add settings-construction tests for boundary and invalid values.

### 12. Session endpoints use expensive full-table and N+1 queries

**Evidence**

- `get_session()` checks existence, then loads every session and scans it in Python (`src/doitall/api/routes/chat.py:309-319`).
- `list_sessions()` calls `message_count()` for every session (`chat.py:284-297`).
- `message_count()` loads all message rows instead of issuing `COUNT(*)` (`session_repository.py:178-180`).
- Session list and detail endpoints have no pagination or message-history limit.

**Impact**

Latency and memory grow rapidly with session count and history size, and one authenticated caller can request the entire database.

**Fix steps**

1. Add `SessionRepository.get(session_id)`.
2. Implement SQL `COUNT(*)` and a grouped count for session listings.
3. Add limit/cursor pagination to session lists and message histories.
4. Add indexes needed by the final query plan, such as `(session_id, created_at)`.
5. Test query counts and pagination boundaries.

### 13. One global API key provides no session or knowledge isolation

**Evidence**

All authenticated users share the same configured key and can list, read, and delete every session. Knowledge and vector-memory collections are also global.

**Impact**

This is acceptable only for a trusted single-user service. It is unsafe as a multi-user or customer-facing platform because there is no ownership boundary.

**Fix steps**

1. Document the current service as single-tenant immediately.
2. Before multi-user deployment, introduce authenticated principals and store `owner_id`/`tenant_id` on sessions, messages, memories, and knowledge chunks.
3. Apply ownership filters to every read, write, search, list, and delete operation.
4. Add cross-tenant denial tests.

### 14. Ingestion metadata has no byte/depth limit

**Evidence**

`src/doitall/api/models.py:75-80` limits metadata to 100 top-level keys but does not limit serialized size, nesting depth, key length, or value types.

**Impact**

A request can submit a very large or deeply nested metadata payload even though document content is bounded. That payload is copied into chunks and sent to Qdrant, amplifying memory, network, and storage use.

**Fix steps**

1. Serialize metadata during validation and enforce a small byte limit.
2. Restrict nesting depth, key length, and allowed scalar/list/object types.
3. Consider storing document metadata once rather than duplicating it in every chunk.
4. Add oversized and deeply nested payload tests.

### 15. Knowledge ingestion is sequential, non-atomic, and non-idempotent

**Evidence**

- `src/doitall/knowledge/vector_repository.py:30-41` embeds and upserts one chunk at a time.
- Chunk IDs are random (`src/doitall/knowledge/chunk.py:11`), so retries create additional points.
- If chunk N fails, chunks 1 through N-1 remain stored while the endpoint reports failure.

**Impact**

Large documents are unnecessarily slow. Retries after partial failures can create duplicate chunks and inconsistent retrieval results.

**Fix steps**

1. Generate deterministic chunk IDs from document ID and chunk index/content hash.
2. Batch embedding and Qdrant upserts.
3. On failure, delete points written for that ingestion or use a staging/version marker and publish only when complete.
4. Add retry and mid-document failure tests.

### 16. Readiness responses expose raw internal exception text

**Evidence**

`src/doitall/api/routes/health.py:31-53` returns `str(exc)` from Qdrant, database, and provider checks on an unauthenticated endpoint.

**Impact**

Exceptions may reveal internal hostnames, database details, provider configuration, or upstream response content.

**Fix steps**

1. Log full exceptions server-side with request/correlation context.
2. Return stable public codes such as `connection_failed` or `not_configured`.
3. Keep liveness public; consider protecting detailed readiness output while retaining a minimal status endpoint for orchestration.

### 17. Metrics and rate-limit state are process-local and unbounded over service lifetime

**Evidence**

`src/doitall/api/app.py:35-36` keeps global in-memory dictionaries. Rate buckets are pruned, but metrics counters have no reset/export lifecycle and disappear on restart. Multi-worker values are inconsistent.

**Impact**

Metrics are incomplete across workers and restarts. The implementation is suitable for development but not reliable production observability.

**Fix steps**

1. Use `prometheus_client` or OpenTelemetry instrumentation.
2. Handle multiprocess workers according to the chosen library’s supported pattern.
3. Add latency histograms and in-flight/error metrics without high-cardinality labels.

### 18. Installed-package runtime paths depend on source layout

**Evidence**

`src/doitall/config/settings.py:13-14` derives `BASE_DIR` with `Path(__file__).resolve().parents[3]`. This points to the repository in a source checkout but can point inside or above a virtual environment for a wheel installation.

**Impact**

Default `data`, `storage`, and `logs` locations can be surprising or unwritable outside an editable source install.

**Fix steps**

1. Make runtime data paths explicitly configurable.
2. Use a platform-appropriate user data directory as the non-container default.
3. In Docker, set absolute `/app/data`, `/app/storage`, and `/app/logs` values explicitly.
4. Add a wheel-install smoke test.

---

## P3 — Maintenance and quality

### 19. The committed tree currently fails CI style gates

**Evidence**

`ruff check` reports four fixable issues, and `ruff format --check` reports five files:

- `src/doitall/database/models.py`
- `src/doitall/models/message.py`
- `tests/agent/test_agent_tool_loop.py`
- `tests/runtime/test_tool_message_builder.py`
- `tests/services/test_conversation_service.py`

**Fix steps**

1. Run `uv run ruff check . --fix`.
2. Run `uv run ruff format .`.
3. Re-run Ruff, mypy, and pytest.
4. Keep pre-commit enabled locally so CI does not discover formatting-only failures.

### 20. Test coverage misses the riskiest integration behavior

The suite is broad but heavily mocked around startup and external systems. Missing regression scenarios include:

- Alembic upgrade followed by tool-message persistence.
- Provider stream failure after partial output.
- Concurrent requests to the same session.
- Unknown provider selection and non-retryable failover.
- Normal stream session metadata.
- Client disconnect during streaming.
- Invalid/rotating authentication headers against rate limits.
- Delayed Qdrant startup and real Compose health behavior.
- Wheel installation and container build/start smoke tests.

Add these tests as each corresponding defect is fixed rather than creating a large test-only phase at the end.

---

# Recommended step-by-step repair plan

## Phase 1 — Restore a trustworthy database and CI baseline

1. Add the missing Alembic migration.
2. Add the migration smoke test.
3. Fix Ruff lint/format violations.
4. Run, in order:
   - `uv run ruff check .`
   - `uv run ruff format --check .`
   - `uv run mypy src`
   - `uv run pytest`
5. Build a temporary database solely through Alembic and run repository tests against it.

**Exit criterion:** both fresh and upgraded databases persist tool messages, and every CI command passes.

## Phase 2 — Make provider and streaming behavior correct

1. Reject unknown providers before session creation.
2. Classify provider exceptions into retryable and non-retryable groups.
3. Define whether explicit provider requests permit cross-provider failover.
4. Prevent failover after the first streamed chunk.
5. Emit session/provider/model metadata before normal stream tokens.
6. Add focused tests for every branch.

**Exit criterion:** one stream contains output from exactly one provider, and clients always know the usable session ID.

## Phase 3 — Serialize session turns safely

1. Add per-session async locks.
2. Define cancellation behavior for streams.
3. Decide and implement slash-command persistence semantics.
4. Test concurrent normal/streaming turns and disconnects.

**Exit criterion:** message ordering is deterministic under concurrent requests, with no phantom sessions.

## Phase 4 — Repair security controls

1. Redesign rate-limit identities so unverified headers cannot create buckets.
2. Stop storing raw credentials in limiter state.
3. Sanitize public readiness details.
4. Document single-tenant limitations or add tenant ownership before multi-user deployment.
5. Move rate limiting to a shared store before scaling beyond one process.

**Exit criterion:** rotating fake credentials does not bypass limits, secrets are not retained as keys, and users cannot cross ownership boundaries in the intended deployment model.

## Phase 5 — Remove event-loop blocking and query amplification

1. Move DB work off the event loop or adopt async SQLAlchemy.
2. Add direct session lookup, SQL counts, grouped counts, and pagination.
3. Measure endpoint latency/query counts with representative data.

**Exit criterion:** slow DB work does not stall unrelated requests, and list/detail query costs remain bounded.

## Phase 6 — Harden ingestion and deployment

1. Validate all operational settings and metadata size/depth.
2. Make chunk IDs deterministic and batch embeddings/upserts.
3. Handle partial ingestion failure safely.
4. Add Qdrant startup health/retry behavior and restart policy.
5. Build and start the Docker image in CI with health checks.
6. Add a wheel-install smoke test and explicit runtime data paths.

**Exit criterion:** retries do not duplicate knowledge, invalid settings fail at startup with clear messages, and the packaged/containerized service starts reproducibly.

---

## Suggested definition of done for each fix

For every item above:

1. Reproduce the defect in a focused failing test.
2. Make the smallest root-cause code change.
3. Run the focused test.
4. Run the affected package tests.
5. Run Ruff and mypy.
6. Run the complete 319+ test suite.
7. Update README/API documentation if the public contract changed.
