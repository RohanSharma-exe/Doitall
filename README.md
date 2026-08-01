# Doitall

> A modular AI application framework for building agents, RAG systems, persistent memory, and multi-provider LLM products.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063)
![License](https://img.shields.io/badge/License-Apache_2.0-blue)

Doitall provides the infrastructure layer most production AI apps need: agent execution, tool calling, chat sessions, semantic memory, knowledge ingestion, vector retrieval, provider adapters, API endpoints, and operational guardrails.

## Table of contents

- [Why Doitall?](#why-doitall)
- [Core capabilities](#core-capabilities)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick start](#quick-start)
- [REST API](#rest-api)
- [Built-in tools](#built-in-tools)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security and production notes](#security-and-production-notes)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

## Why Doitall?

LLM applications usually need more than one model call. They need reliable context assembly, safe tools, provider portability, persistence, retrieval, APIs, and production controls. Doitall packages those concerns behind clear abstractions so you can build AI products instead of repeatedly rebuilding infrastructure.

## Core capabilities

### Agents and tools

- Agent runtime with a system prompt, conversation context, and tool-calling loop.
- Built-in skill registry and tool executor.
- Persisted tool-call and tool-result messages.
- Extensible `BaseSkill` interface for custom tools.

### Memory and RAG

- Long-term vector memory backed by Qdrant.
- Development-friendly in-memory store abstractions.
- Knowledge ingestion service for chunking, embedding, and indexing documents.
- TXT, Markdown, and recursive directory loaders.
- Isolated Qdrant collections for memories and knowledge chunks.

### Provider abstraction

- Provider manager with default-provider selection.
- OpenAI, Gemini, Groq, Anthropic, Ollama, and OpenRouter adapters.
- Per-request provider and model overrides.
- Shared response, usage, and tool-call normalization.

### REST API and sessions

- FastAPI app with chat, streaming chat, knowledge ingestion, provider listing, command listing, system, health, metrics, and session endpoints.
- SQLite-backed session and message persistence through SQLModel/SQLAlchemy.
- Hot in-process session cache for active conversations.
- Request IDs and structured request logs.

### Production controls

- Optional API-key protection for mutating endpoints.
- Configurable CORS origins.
- Bounded chat and ingestion payload sizes.
- In-process fixed-window rate limiting.
- Prometheus-compatible HTTP request metrics.
- Liveness and readiness probes.
- Production startup guardrails for debug mode, wildcard CORS, and missing API keys.
- Filesystem tool write/delete disabled by default.

## Architecture

```text
User message
  -> ChatService
  -> ContextAssembler
       -> ConversationProvider  (recent session history)
       -> MemoryProvider        (semantic memory retrieval)
       -> KnowledgeProvider     (RAG retrieval)
       -> ToolProvider          (registered skill schemas)
  -> PromptBuilder
  -> LLM Provider
  -> AgentExecutor              (tool loop)
  -> MemoryPipeline             (extract, filter, score, store)
  -> Response
```

Source layout:

```text
src/doitall/
├── agent/          Agent model, manager, executor, and factory
├── api/            FastAPI app, routes, errors, and API models
├── commands/       Slash-command registry
├── config/         Settings, constants, and logging setup
├── core/           Bootstrap, application wiring, and shared exceptions
├── database/       SQLModel models, sessions, repository, and migrations helpers
├── embeddings/     Embedding manager and LiteLLM embedding service
├── knowledge/      Documents, chunks, loaders, ingestion, and vector repository
├── memory/         Memory models, stores, Qdrant repositories, and vector stores
├── models/         Domain models for messages, prompts, tools, sessions, and usage
├── providers/      LLM provider adapters and provider manager
├── runtime/        Context, prompt, memory, knowledge, tool, and execution pipeline
├── security/       API-key auth and permission helpers
├── serialization/  Serializers for chunks, messages, and memories
├── services/       Chat, conversation, tool-calling, and DI services
├── skills/         Skill base classes, registry, manager, and built-ins
└── workspace/      Sandboxed workspace filesystem abstraction
```

## Requirements

- Python 3.14 or newer.
- [`uv`](https://docs.astral.sh/uv/) for dependency management.
- Qdrant for vector-backed memory and knowledge retrieval.
- At least one provider API key, unless you are using a local provider such as Ollama.

## Installation

```bash
git clone <your-repository-url> doitall
cd doitall
uv sync
```

For development dependencies:

```bash
uv sync --dev
```

## Configuration

Doitall reads settings from environment variables and `.env`.

```env
# Application
APP_NAME=Doitall
APP_VERSION=0.1.0
ENVIRONMENT=development
DEBUG=true

# API
API_HOST=127.0.0.1
API_PORT=8000
API_KEY=
METRICS_REQUIRE_API_KEY=false
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://localhost:5173"]

# Limits and safety
SESSION_TTL_SECONDS=3600
MAX_HISTORY_MESSAGES=50
CHAT_MESSAGE_MAX_LENGTH=10000
INGEST_CONTENT_MAX_LENGTH=100000
RATE_LIMIT_ENABLED=true
CHAT_RATE_LIMIT_PER_MINUTE=60
INGEST_RATE_LIMIT_PER_MINUTE=20
ENABLE_FILESYSTEM_WRITE_TOOLS=false
FILESYSTEM_MAX_READ_BYTES=1000000
FILESYSTEM_MAX_LIST_ENTRIES=500

# Database
DATABASE_URL=sqlite:///storage/doitall.db

# Vector storage and embeddings
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
EMBEDDING_MODEL=text-embedding-3-large

# Providers
DEFAULT_PROVIDER=gemini
OPENAI_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
NVIDIA_API_KEY=
OPENROUTER_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# Default models
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini/gemini-2.5-flash
GROQ_MODEL=groq/llama-3.3-70b-versatile
ANTHROPIC_MODEL=anthropic/claude-3-5-sonnet-20241022
NVIDIA_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1
OLLAMA_MODEL=ollama/llama3.2
OPENROUTER_MODEL=openrouter/anthropic/claude-3.5-sonnet

# LLM timeout
LLM_TIMEOUT_SECONDS=30
```

> In production, set `ENVIRONMENT=production`, `DEBUG=false`, a strong `API_KEY`, explicit `CORS_ORIGINS`, and the provider/vector-store credentials your deployment requires.

## Quick start

Run the CLI help:

```bash
uv run doitall --help
```

Start an interactive terminal chat:

```bash
uv run doitall chat
```

Run diagnostics:

```bash
uv run doitall doctor
```

Start the REST API:

```bash
uv run doitall start --host 127.0.0.1 --port 8000
```

Open interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## REST API

### Chat

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is 12 * 9?","provider":"gemini"}'
```

The response includes a `session_id`. Pass it on later requests to continue the same persisted conversation:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<session-id>","message":"What did I just ask?"}'
```

### Streaming chat

```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"Explain Doitall in one paragraph","provider":"gemini"}'
```

The SSE stream emits session metadata, user-visible progress events, token chunks, a final done event, and error events when needed. Doitall does not expose hidden model chain-of-thought.

### Knowledge ingestion

```bash
curl -X POST http://127.0.0.1:8000/v1/knowledge/ingest \
  -H 'Content-Type: application/json' \
  -d '{"title":"Notes","content":"Doitall stores RAG chunks in Qdrant."}'
```

### Sessions

```bash
curl http://127.0.0.1:8000/v1/sessions
curl http://127.0.0.1:8000/v1/sessions/<session-id>
curl -X DELETE http://127.0.0.1:8000/v1/sessions/<session-id>
```

### Health and metrics

```bash
curl http://127.0.0.1:8000/v1/health/live
curl http://127.0.0.1:8000/v1/health/ready
curl http://127.0.0.1:8000/metrics
```

## Built-in tools

- `calculator` — safe arithmetic evaluation.
- `filesystem` — workspace read/list/exists actions, plus write/delete only when `ENABLE_FILESYSTEM_WRITE_TOOLS=true`.
- `time` — current date/time for an IANA timezone such as `UTC` or `America/New_York`.

## Development

Format code:

```bash
uv run ruff format .
```

Lint code:

```bash
uv run ruff check .
```

Run tests:

```bash
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/api/test_sessions_endpoints.py
```

## Testing

The test suite covers API routes, provider adapters, domain models, tools, services, knowledge ingestion, database sessions, commands, and bootstrap behavior.

Recommended local check before opening a PR:

```bash
uv run ruff format . --check
uv run ruff check .
uv run pytest
```

## Deployment

This repository includes Docker and Docker Compose support.

```bash
export API_KEY='replace-me-with-a-strong-secret'
docker compose up --build
```

The Compose stack starts:

- the Doitall API on port `8000`;
- Qdrant on port `6333`;
- persistent volumes for API storage and Qdrant data.

For production deployments, configure explicit CORS origins, provider API keys, vector-store credentials, persistent database storage, and `DEBUG=false`.

## Security and production notes

- Set `API_KEY` to protect mutating endpoints.
- Set `METRICS_REQUIRE_API_KEY=true` when metrics should not be public.
- Keep `ENABLE_FILESYSTEM_WRITE_TOOLS=false` unless you intentionally want LLM-exposed filesystem write/delete actions inside the workspace.
- Do not use wildcard CORS in production.
- The built-in rate limiter is in-process and best suited for single-process deployments. Use Redis or another shared store for multi-replica rate limiting.
- HTTP metrics use route templates to avoid high-cardinality labels for dynamic routes.
- `/v1/health/live` is a fast liveness probe. `/v1/health/ready` checks dependencies and returns `503` when dependencies are unavailable.

## Roadmap

Completed foundations:

- Agent execution with tool-calling loops.
- Runtime context assembly.
- Vector-backed memory and RAG knowledge retrieval.
- Multi-provider LLM abstraction.
- Persisted chat sessions and messages.
- API endpoints for chat, streaming chat, sessions, commands, providers, health, metrics, and knowledge ingestion.
- Optional API-key auth, payload limits, rate limiting, request IDs, and production startup guardrails.

Planned improvements:

- Redis-backed distributed rate limiting.
- Provider connectivity health checks.
- Streaming implementations across all provider adapters.
- Additional loaders for PDF, HTML, DOCX, and GitHub repositories.
- Per-agent permission scopes for tools.
- OpenTelemetry tracing and Prometheus metrics expansion.
- MCP and plugin lifecycle integration.
- Multi-agent orchestration.

## Contributing

Contributions are welcome. Before submitting a pull request, run formatting, linting, and tests, and include a clear summary of the change and any operational impact.

## License

Apache-2.0
