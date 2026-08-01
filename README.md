# 🚀 Doitall

> A production-first AI framework for building intelligent agents, RAG systems, persistent memory, and AI-powered applications.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Tests](https://img.shields.io/badge/Tests-see%20test%20suite-informational)
![Code%20Style](https://img.shields.io/badge/Ruff-Clean-brightgreen)
![License](https://img.shields.io/badge/License-Apache_2.0-blue)

---

## Vision

Doitall is an open-source framework designed to make building AI applications simple, modular, and production-ready.

Instead of focusing only on LLM calls, Doitall provides the complete infrastructure required for real-world AI systems:

| | |
|---|---|
| 🤖 | Agents with tool-calling loops |
| 🧠 | Long-term semantic memory (Qdrant) |
| 📚 | Knowledge bases with RAG retrieval |
| 🔎 | Semantic search & embeddings |
| ⚡ | Isolated vector collections per domain |
| 🔌 | Multiple AI providers (Gemini, Groq, …) |
| 🛠 | Tool / Skill execution engine |
| 💬 | Multi-turn conversation management |
| 📄 | Document ingestion pipeline |
| 🚀 | Async-first, extensible architecture |

---

## How It Works

```
User Input
  → ChatService
  → ContextAssembler
       ├── ConversationProvider  →  past messages
       ├── MemoryProvider        →  relevant memories  (semantic search)
       ├── KnowledgeProvider     →  relevant documents (RAG retrieval)
       └── ToolProvider          →  available tools
  → PromptBuilder  →  system + memory + knowledge + messages
  → LLM Provider   →  Gemini / Groq / …
  → AgentExecutor  →  tool loop until final answer
  → MemoryPipeline →  extract → filter → score → store
  → Response
```

---

## Quick Start

```bash
# Install
git clone https://github.com/your-org/doitall
cd doitall
uv sync

# Configure
cp .env.example .env
# Set DEFAULT_PROVIDER, provider API keys, QDRANT_URL, EMBEDDING_MODEL, etc.

# Run
uv run python -m doitall

# Or start the REST API
uv run doitall start
```

> Note: if `.env.example` is not present in your checkout, create `.env`
> with the settings shown in the Configuration section below.

---

## Features

### ✅ Agent System
- Agent model with name, system prompt, and persona
- `AgentManager` for agent lifecycle
- `AgentExecutor` with multi-turn tool loop
- Tool-call → execute → continue loop (full agentic cycle)

### ✅ Memory System
- `MemoryManager` with dual-backend support
- `InMemoryStore` for development/testing
- `VectorMemoryStore` backed by Qdrant for semantic retrieval
- `MemoryPipeline`: extract → filter → score → persist after every turn
- Stored in the `"memories"` Qdrant collection

### ✅ Knowledge System (RAG)
- `VectorKnowledgeRepository` — chunk, embed, index, and search documents
- `KnowledgeIngestionService` — end-to-end document ingest pipeline
- `SimpleChunker` — splits documents into indexable chunks
- **Loaders**: TXT, Markdown, recursive directory
- `KnowledgeProvider` — injects semantically relevant docs into context
- Stored in the `"knowledge"` Qdrant collection (isolated from memory)

### ✅ Embeddings
- `EmbeddingManager` with `LiteLLMEmbeddingService`
- Batch embedding support
- Provider-agnostic abstraction

### ✅ Providers
- `GeminiProvider` — chat, tool calling, response normalization
- `GroqProvider` — chat, tool calling, response normalization
- `OpenAIProvider`, `AnthropicProvider`, `OllamaProvider`, and `OpenrouterProvider`
  are registered provider adapters
- `DEFAULT_PROVIDER` controls the bootstrapped default provider
- Chat requests can override the provider per request
- `BaseProvider` — abstract base; missing `chat()` fails at class load time
- `LiteLLMClient` — shared client with typed error translation

### ✅ Tool / Skill System
- `SkillRegistry` + `SkillManager` — register and resolve skills by name
- `ToolCallingEngine` + `ToolExecutor` — execute tool calls from LLM responses
- **Built-in skills**: `CalculatorSkill`, `FilesystemSkill`
- Pluggable — add any skill by subclassing `BaseSkill`

### ✅ Runtime Pipeline
- `ContextAssembler` — async provider dispatch with `RuntimeContext`
- `PromptBuilder` — builds system + memory + knowledge + message prompt
- `RuntimeExecutor` — sends prepared messages to LLM provider
- `ToolMessageBuilder` — formats tool results for LLM re-submission
- API chat sessions reuse conversation state by `session_id` for the current
  process lifetime

### ✅ Core Infrastructure
- `bootstrap()` — single DI wiring function; correct instantiation order
- `ServiceContainer` — lightweight DI container
- Pydantic v2 models throughout
- Loguru structured logging
- `Workspace` — sandboxed file I/O
- Optional API-key protection for mutating endpoints
- Filesystem write/delete tool actions are disabled unless explicitly enabled

---

## Configuration

Common `.env` values:

```env
DEFAULT_PROVIDER=gemini

GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
EMBEDDING_MODEL=text-embedding-3-large

DATABASE_URL=sqlite:///storage/doitall.db

# Optional. When set, POST /v1/chat and POST /v1/knowledge/ingest require
# either Authorization: Bearer <key> or X-API-Key: <key>.
API_KEY=

# Keep false for production unless you intentionally want the LLM-exposed
# filesystem tool to write/delete files inside the workspace.
ENABLE_FILESYSTEM_WRITE_TOOLS=false
```

---

## REST API

Start the server:

```bash
uv run doitall start --host 127.0.0.1 --port 8000
```

Open docs:

```text
http://127.0.0.1:8000/docs
```

Send a chat message:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is 12 * 9?","provider":"gemini"}'
```

Continue the same in-process session by passing the returned `session_id`:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<session-id>","message":"What did I just ask?"}'
```

Ingest a knowledge document:

```bash
curl -X POST http://127.0.0.1:8000/v1/knowledge/ingest \
  -H 'Content-Type: application/json' \
  -d '{"title":"Notes","content":"Doitall stores RAG chunks in Qdrant."}'
```

The ingestion response includes the `document_id`, `chunk_count`, and status.

---

## Architecture

```
src/doitall/

├── agent/          Agent model, executor, tool loop
├── api/            REST API layer
├── config/         Settings (pydantic-settings), logging
├── core/           bootstrap(), DI container
├── database/       SQLAlchemy session (persistence planned)
├── embeddings/     EmbeddingManager, LiteLLM service
├── knowledge/      Document, Chunk, loaders, ingestion, vector repo
├── memory/         MemoryStore, QdrantRepository, VectorMemoryStore
├── mcp/            MCP integration (planned)
├── models/         Domain models: Message, Memory, Document, ToolCall, …
├── parsers/        Text parser abstraction
├── plugins/        Plugin lifecycle (planned)
├── providers/      Gemini, Groq, base, LiteLLM client
├── runtime/        ContextAssembler, providers, PromptBuilder, executor
├── security/       Optional API key auth, permissions (planned)
├── serialization/  MemorySerializer, ChunkSerializer
├── services/       ChatService, ConversationService, ToolCallingEngine
├── skills/         SkillRegistry, manager, BaseSkill, built-ins
└── workspace/      Sandboxed filesystem access
```

---

## Tech Stack

| Tool | Role |
|---|---|
| Python 3.14 | Runtime |
| Pydantic v2 | Models and validation |
| LiteLLM | Unified LLM provider client |
| Qdrant | Vector database (memory + knowledge) |
| Loguru | Structured logging |
| Ruff | Linting and formatting |
| Pytest + pytest-asyncio | Testing |
| uv | Package management |

---

## Testing

```bash
uv run pytest          # run the test suite
uv run ruff check .    # lint
uv run ruff format .   # format
```

The test suite covers agent, memory, knowledge, runtime, providers, services,
skills, serialization, API models, and workspace behavior.

---

## Roadmap

### ✅ Complete
- Agent system with tool loop
- Async context assembly pipeline
- Long-term memory (semantic + in-memory)
- RAG knowledge system with isolated vector collections
- Embedding layer
- Multi-provider support (Gemini, Groq)
- Tool / skill execution engine
- Document loaders (TXT, Markdown, directory)
- DI container + bootstrap
- REST API routes for chat, health, provider listing, and knowledge ingestion
- Optional API-key authentication for mutating endpoints
- Per-request provider overrides
- In-process session reuse by `session_id`
- Knowledge ingestion responses with chunk counts

### 🔥 Next (Phase 1 — Production Hardening)
- [ ] Persist chat sessions beyond process memory
- [ ] Real provider health checks that validate credentials/connectivity
- [ ] Conversation persistence (SQLite/Postgres via `database/`)
- [ ] Real `MemoryFilter` (min-length, deduplication)
- [ ] Real `MemoryScorer` (embedding similarity)
- [ ] Per-agent permission scoping for tools

### 📡 Phase 2 — REST API
- [x] FastAPI routes: `POST /chat`, `GET /health`, `GET /providers`, `POST /knowledge/ingest`
- [ ] Streaming endpoint (`POST /chat/stream` with SSE)
- [x] Pydantic request/response schemas

### 🔐 Phase 3 — Security
- [x] Optional API key authentication
- [ ] Per-agent permission scoping
- [ ] Rate limiting

### 📄 Phase 4 — More Loaders
- [ ] PDF loader
- [ ] HTML / web page loader
- [ ] DOCX loader
- [ ] GitHub repo loader

### 🌊 Phase 5 — Streaming
- [ ] `BaseProvider.stream()` implementation
- [ ] `ChatService.stream_chat()` generator
- [ ] API streaming endpoint

### 🤖 Phase 6 — Multi-Agent
- [ ] Agent orchestrator
- [ ] Agent-to-agent messaging
- [ ] Shared memory pool with per-agent namespacing

### 🔌 Phase 7 — MCP + Plugins
- [ ] Model Context Protocol adapter
- [ ] Plugin lifecycle (load → init → register → teardown)

### 📊 Phase 8 — Observability
- [ ] OpenTelemetry spans on LLM calls
- [ ] Token count + latency tracking
- [ ] Prometheus metrics export

---

## Development

```bash
# Format
uv run ruff format .

# Lint
uv run ruff check .

# Test
uv run pytest

# Test with output
uv run pytest -v

# Run a single test file
uv run pytest tests/runtime/test_context_assembler.py
```

---

## Philosophy

> Build infrastructure once. Build AI applications forever.

Doitall is designed to be the foundation under your AI application — not a demo, not a prototype, but a real framework with proper abstractions, async pipelines, isolated storage, and a growing test suite.

---

## Contributing

Contributions, issues, and discussions are welcome.

If you're working on AI agents, RAG systems, LLM infrastructure, or production AI engineering, open an issue or submit a pull request.

---

⭐ Star the repository if you find it useful!

---

## Production Readiness

Doitall now includes the core production controls from the readiness roadmap:

- **Persistent sessions**: chat sessions and messages are stored in SQLite via SQLModel, with Alembic migration scaffolding for schema history.
- **Bounded context**: full history remains available through the session APIs, while provider prompts use a configurable sliding window (`MAX_HISTORY_MESSAGES`) to reduce context-window failures.
- **Input validation**: chat and ingestion payloads have bounded lengths (`CHAT_MESSAGE_MAX_LENGTH`, `INGEST_CONTENT_MAX_LENGTH`) plus metadata limits.
- **Rate limiting**: `/v1/chat`, `/v1/chat/stream`, and `/v1/knowledge/ingest` have configurable in-process fixed-window limits. For multi-replica production deployments, replace the in-process limiter with Redis or another shared store.
- **Request tracing**: every API response includes `X-Request-ID`; incoming `X-Request-ID` values are preserved when supplied.
- **Structured request logs**: request method, path, status, latency, and request ID are logged for correlation.
- **Metrics**: `/metrics` exposes basic Prometheus-compatible HTTP request counters.
- **Health probes**: `/v1/health/live` is a fast liveness check; `/v1/health/ready` checks dependencies and returns `503` when not ready. `/v1/health` remains as a backward-compatible readiness alias.
- **Production guardrails**: startup refuses `ENVIRONMENT=production` when `DEBUG=true`, wildcard CORS is configured, or `API_KEY` is missing.
- **Docker deployment**: `Dockerfile` and `docker-compose.yml` run the API with Qdrant and persistent volumes.

### Streaming chat and progress events

Use the SSE endpoint for lower-latency responses:

```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"Explain Doitall in one paragraph","provider":"gemini"}'
```

The stream sends:

- `event: session` with the session ID.
- `data:` chunks containing assistant text as it arrives.
- `event: done` when complete.
- `event: error` if provider execution fails.

Doitall does **not** expose hidden model chain-of-thought. If you want user-visible progress, build UI affordances around the SSE `session`, chunk, `done`, and `error` events, and around tool-call/result messages that are safe to show.

### Built-in tools

Built-in tools currently include:

- `calculator` — safe arithmetic evaluation.
- `filesystem` — workspace read/list/exists plus optional write/delete when `ENABLE_FILESYSTEM_WRITE_TOOLS=true`.
- `time` — current date/time for an IANA timezone such as `UTC` or `America/New_York`.

---

## CI on GitHub

This repo includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs automatically on pushes and pull requests:

1. Checks out the repository.
2. Installs `uv`.
3. Installs Python 3.14.
4. Installs locked project dependencies with `uv sync --dev --frozen`.
5. Runs `uv run ruff check .`.
6. Runs `uv run pytest`.

If your default branch is not `main`, `master`, or `work`, update the workflow branch list.

---

## Deployment with Docker Compose

```bash
export API_KEY='replace-me'
docker compose up --build
```

The Compose stack starts:

- `api` on port `8000`.
- `qdrant` on port `6333`.
- Persistent volumes for API storage and Qdrant data.

For production, set explicit `CORS_ORIGINS`, provider API keys, `DEFAULT_PROVIDER`, and keep `DEBUG=false`.
