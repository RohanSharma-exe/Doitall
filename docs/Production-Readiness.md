# Production Readiness

This checklist defines the minimum checks to run before promoting Doitall to a production environment.

## Required local quality gates

Run these commands from the repository root:

```bash
uv sync
uv run ruff format . --check
uv run ruff check .
uv run pytest
```

All commands must exit with status code `0` before release.

## Recommended release validation

In addition to the required gates, validate the following in an environment that mirrors production:

1. **Configuration**
   - Set `ENVIRONMENT=production`.
   - Set a strong `API_KEY` for protected API routes.
   - Set `ENABLE_FILESYSTEM_WRITE_TOOLS=false` unless file write/delete tool access is explicitly required.
   - Configure provider API keys only for enabled providers.
   - Configure `DATABASE_URL` and `QDRANT_URL` to durable services.

2. **Database**
   - Apply migrations before starting the API.
   - Confirm session creation, session listing, session lookup, and session deletion work against the production database.

3. **Vector storage**
   - Confirm Qdrant is reachable from the API host.
   - Confirm the memory and knowledge collections use an embedding size compatible with `EMBEDDING_MODEL`.

4. **LLM providers**
   - Run the API health endpoint.
   - Send one chat request through each enabled provider.
   - Exercise one tool-calling request, such as a calculator request, and verify the session history includes the user message, tool call, tool result, and final answer.

5. **Streaming**
   - Test `/v1/chat/stream` with normal chat.
   - Test `/v1/chat/stream` when tools are available. The service intentionally uses the non-streaming tool loop fallback so tool calls are executed and persisted instead of being ignored.

6. **Operational checks**
   - Verify logs are written at the expected `LOG_LEVEL`.
   - Verify process supervision restarts the API on failure.
   - Verify network/firewall rules restrict database and Qdrant access.
   - Verify secrets are injected through environment variables or a secrets manager, not committed files.

## Known non-blocking warnings

The test suite may emit a Qdrant compatibility warning when a local Qdrant daemon is not available. The tests mock or isolate vector behavior, so this warning does not fail the suite. Production environments should still validate real Qdrant connectivity before release.
