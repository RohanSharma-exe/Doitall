# 🚀 Doitall

> A production-first AI framework for building intelligent agents, RAG systems, persistent memory, and AI-powered applications.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Tests](https://img.shields.io/badge/Tests-169%20Passing-success)
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
# Set GEMINI_API_KEY, QDRANT_URL, EMBEDDING_MODEL, etc.

# Run
uv run python -m doitall
```

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

### ✅ Core Infrastructure
- `bootstrap()` — single DI wiring function; correct instantiation order
- `ServiceContainer` — lightweight DI container
- Pydantic v2 models throughout
- Loguru structured logging
- `Workspace` — sandboxed file I/O

---

## Architecture

```
src/doitall/

├── agent/          Agent model, executor, tool loop
├── api/            REST API layer (planned)
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
├── security/       Auth, permissions (planned)
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
uv run pytest          # 169 tests, all passing
uv run ruff check .    # lint
uv run ruff format .   # format
```

Current coverage: **169 tests** across agent, memory, knowledge, runtime, providers, services, and skills modules.

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
- 169-test suite

### 🔥 Next (Phase 1 — Production Hardening)
- [ ] OpenAI provider implementation
- [ ] Anthropic provider implementation
- [ ] Conversation persistence (SQLite/Postgres via `database/`)
- [ ] Real `MemoryFilter` (min-length, deduplication)
- [ ] Real `MemoryScorer` (embedding similarity)
- [ ] Bootstrap singleton guard (prevent double-init)
- [ ] `Doitall.start()` / `stop()` lifecycle hooks

### 📡 Phase 2 — REST API
- [ ] FastAPI routes: `POST /chat`, `GET /health`, `POST /knowledge/ingest`
- [ ] Streaming endpoint (`POST /chat/stream` with SSE)
- [ ] Pydantic request/response schemas

### 🔐 Phase 3 — Security
- [ ] API key authentication
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
