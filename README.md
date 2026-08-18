# Doitall

> A modular AI application framework for building agents, RAG systems, persistent memory, tool-enabled workflows, and multi-provider LLM applications.

![Python](https://img.shields.io/badge/Python-3.14+-blue)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063)
![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-red)
![License](https://img.shields.io/badge/License-Apache--2.0-blue)

Doitall is a Python-based AI application framework that provides the infrastructure needed to build production-oriented LLM applications without rebuilding the same foundations for every project.

It combines:

* Agent execution
* Tool calling
* Persistent conversations
* Semantic memory
* RAG knowledge retrieval
* Multiple LLM providers
* FastAPI APIs
* Streaming responses
* Authentication
* Rate limiting
* Request IDs
* Health checks
* Metrics
* Docker deployment
* Database persistence
* Extensible skills and tools

## ⚠️ Project Status

**Status: Active development / pre-production**

Doitall has a working application architecture, REST API, persistent sessions, RAG infrastructure, multiple provider adapters, Docker support, CI, and automated tests.

It is suitable for:

* Personal AI applications
* Internal AI services
* Prototypes
* Agent experiments
* AI backend development
* Self-hosted deployments

Before using Doitall as a public multi-user SaaS, additional production hardening is recommended, particularly around distributed rate limiting, authentication, database migrations, observability, provider health checks, and deployment infrastructure.

---

## Why Doitall?

Most AI applications eventually need much more than an LLM API call.

A real application needs:

```text
User
  ↓
API
  ↓
Authentication
  ↓
Session
  ↓
Context
  ├── Conversation history
  ├── Semantic memory
  ├── RAG knowledge
  └── Available tools
  ↓
Agent
  ↓
LLM Provider
  ↓
Tool execution
  ↓
Memory pipeline
  ↓
Response
```

Doitall provides these building blocks behind reusable abstractions.

---

## Core Features

### 🤖 Agents

* Agent abstraction with system prompts
* Conversation-aware execution
* Tool-calling loops
* Configurable tool iteration limits
* Tool-call limits
* Repeated-tool-call protection
* Extensible agent architecture

### 🛠️ Tools and Skills

Built-in skill registry with an extensible `BaseSkill` interface.

Current built-in tools include:

| Tool         | Description                          |
| ------------ | ------------------------------------ |
| `calculator` | Safe arithmetic operations           |
| `filesystem` | Workspace-scoped file operations     |
| `time`       | Current date/time for IANA timezones |

Filesystem write/delete operations are disabled by default.

---

### 🧠 Persistent Memory

Doitall supports semantic memory using Qdrant.

```text
Conversation
     ↓
Memory extraction
     ↓
Filtering
     ↓
Scoring
     ↓
Embedding
     ↓
Qdrant
```

Memory and knowledge documents use separate vector collections.

---

### 📚 RAG / Knowledge

Knowledge ingestion supports:

* Text
* Markdown
* Recursive directory loading
* Chunking
* Embedding
* Vector indexing
* Semantic retrieval

Current vector backend:

**Qdrant**

Planned loaders include:

* PDF
* HTML
* DOCX
* GitHub repositories

---

### 🔌 LLM Providers

Doitall currently provides adapters for:

* Gemini
* Groq
* OpenAI
* Anthropic
* OpenRouter
* Ollama

Provider selection is abstracted behind a common provider interface.

This allows applications to switch providers without rewriting the agent runtime.

> Provider availability depends on configured credentials and implementation support. Check the configuration section before selecting a provider.

---

## Architecture

```text
                         ┌──────────────────┐
                         │      Client      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              Authentication   Sessions      Rate Limit
                    │             │
                    └─────────────┼─────────────┘
                                  ▼
                         ┌──────────────────┐
                         │   Chat Service   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Context Assembly │
                         └────────┬─────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
          Conversation        Memory          Knowledge
             Store            Store             RAG
                 │                │                │
                 └────────────────┼────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Prompt Builder  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   LLM Provider   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Agent Executor  │
                         └────────┬─────────┘
                                  │
                                  ▼
                              Tools
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Memory Pipeline  │
                         └────────┬─────────┘
                                  │
                                  ▼
                              Response
```

---

## Project Structure

```text
Doitall/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
├── migrations/
├── src/
│   └── doitall/
│       ├── agent/
│       ├── api/
│       ├── commands/
│       ├── config/
│       ├── core/
│       ├── database/
│       ├── embeddings/
│       ├── knowledge/
│       ├── memory/
│       ├── models/
│       ├── providers/
│       ├── runtime/
│       ├── security/
│       ├── serialization/
│       ├── services/
│       ├── skills/
│       └── workspace/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Requirements

* Python 3.14+
* [uv](https://docs.astral.sh/uv/)
* Qdrant
* At least one configured LLM provider
* An embedding provider/model for semantic memory and RAG

For production deployments, PostgreSQL and managed Qdrant are recommended over local development services.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/RohanSharma-exe/Doitall.git
cd Doitall
```

Install dependencies:

```bash
uv sync
```

Install development dependencies:

```bash
uv sync --dev
```

---

## Configuration

Create your local environment file:

```bash
copy .env.example .env
```

Then configure the required values.

### Application

```env
APP_NAME=Doitall
APP_VERSION=0.1.0
ENVIRONMENT=development
DEBUG=true
```

### API

```env
API_HOST=127.0.0.1
API_PORT=8000

API_KEY=

CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Database

Development:

```env
DATABASE_URL=sqlite:///storage/doitall.db
```

Production:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/doitall
```

### Qdrant

Local:

```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

Production:

```env
QDRANT_URL=https://your-qdrant-instance
QDRANT_API_KEY=your-secret
```

### Embeddings

Example:

```env
EMBEDDING_MODEL=text-embedding-3-large
```

Make sure the provider required by the selected embedding model is configured.

### LLM Providers

Gemini:

```env
DEFAULT_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini/gemini-2.5-flash
```

OpenAI:

```env
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o
```

Groq:

```env
GROQ_API_KEY=your-key
GROQ_MODEL=groq/llama-3.3-70b-versatile
```

Anthropic:

```env
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=anthropic/claude-3-5-sonnet-20241022
```

OpenRouter:

```env
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openrouter/anthropic/claude-3.5-sonnet
```

Ollama:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=ollama/llama3.2
```

---

## Quick Start

Run diagnostics:

```bash
uv run doitall doctor
```

Start the CLI:

```bash
uv run doitall chat
```

Start the API:

```bash
uv run doitall start --host 127.0.0.1 --port 8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

## REST API

### Chat

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"What is 12 * 9?\",\"provider\":\"gemini\"}"
```

If API authentication is enabled:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d "{\"message\":\"Hello\"}"
```

A successful response returns a `session_id`.

Continue an existing conversation:

```bash
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"SESSION_ID\",\"message\":\"What did I just ask?\"}"
```

---

### Streaming Chat

```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Explain Doitall\"}"
```

The endpoint uses Server-Sent Events.

Events include:

```text
session
token
done
error
```

Doitall does not expose hidden model chain-of-thought.

---

### Knowledge Ingestion

```bash
curl -X POST http://127.0.0.1:8000/v1/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Notes\",\"content\":\"Doitall provides AI application infrastructure.\"}"
```

---

### Sessions

List sessions:

```bash
curl http://127.0.0.1:8000/v1/sessions
```

Get a session:

```bash
curl http://127.0.0.1:8000/v1/sessions/SESSION_ID
```

Delete a session:

```bash
curl -X DELETE http://127.0.0.1:8000/v1/sessions/SESSION_ID
```

---

## Health Endpoints

Liveness:

```text
GET /v1/health/live
```

Readiness:

```text
GET /v1/health/ready
```

Backward-compatible health endpoint:

```text
GET /v1/health
```

Metrics:

```text
GET /metrics
```

### Liveness vs Readiness

**Liveness** answers:

> Is the API process alive?

**Readiness** answers:

> Can the API currently serve requests?

Readiness checks include:

* Database
* Qdrant
* Provider configuration

---

## Security

Doitall includes several application-level security controls.

### API key authentication

Set:

```env
API_KEY=your-strong-secret
```

Clients can authenticate using:

```http
Authorization: Bearer YOUR_API_KEY
```

or:

```http
X-API-Key: YOUR_API_KEY
```

### Filesystem protection

Filesystem write/delete operations are disabled by default:

```env
ENABLE_FILESYSTEM_WRITE_TOOLS=false
```

The workspace abstraction restricts filesystem operations to the configured workspace.

### Request limits

Configure:

```env
CHAT_MESSAGE_MAX_LENGTH=10000
INGEST_CONTENT_MAX_LENGTH=100000
FILESYSTEM_MAX_READ_BYTES=1000000
FILESYSTEM_MAX_LIST_ENTRIES=500
```

### Rate limiting

Development uses an in-process fixed-window limiter.

For multi-instance production deployments, use a distributed rate limiter such as Redis.

---

## Docker

Build the image:

```bash
docker build -t doitall .
```

Run the application with Docker Compose:

```bash
docker compose up --build
```

The default Compose deployment provides:

```text
Doitall API
    ↓
port 8000

Qdrant
    ↓
port 6333
```

API:

```text
http://localhost:8000
```

Documentation:

```text
http://localhost:8000/docs
```

---

## Production Deployment

Doitall is designed to be containerized.

A recommended production architecture is:

```text
                    Internet
                       │
                       ▼
                 Reverse Proxy
                       │
                       ▼
              ┌─────────────────┐
              │   Doitall API   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     PostgreSQL      Qdrant       Redis
     Sessions        RAG          Rate limits
```

Recommended production components:

* Docker
* PostgreSQL
* Qdrant/Qdrant Cloud
* Redis
* HTTPS reverse proxy
* Secret management
* Centralized logging
* Monitoring
* Distributed rate limiting

### Production environment

Always use:

```env
ENVIRONMENT=production
DEBUG=false
API_KEY=strong-random-secret
```

Use explicit CORS origins:

```env
CORS_ORIGINS=["https://your-frontend.example.com"]
```

Do not use:

```env
CORS_ORIGINS=["*"]
```

for a production application.

---

## Database Migrations

Doitall uses Alembic for schema migrations.

Create a migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Check current migration:

```bash
uv run alembic current
```

Production deployments should run database migrations as an explicit deployment step before starting the API.

---

## Development

Format:

```bash
uv run ruff format .
```

Check formatting:

```bash
uv run ruff format --check .
```

Lint:

```bash
uv run ruff check .
```

Type check:

```bash
uv run mypy src
```

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=doitall
```

---

## CI

GitHub Actions currently checks:

* Ruff linting
* Ruff formatting
* mypy type checking
* pytest

Recommended production CI additionally includes:

* Docker build
* Docker smoke test
* Database migration test
* API integration tests
* Dependency vulnerability scanning
* Coverage enforcement

---

## Observability

Doitall provides:

* Request IDs
* Structured application logging
* HTTP request metrics
* Liveness checks
* Readiness checks
* Provider information

A production deployment should additionally add:

* OpenTelemetry
* Distributed tracing
* Centralized logs
* Alerting
* Error tracking
* Database monitoring
* LLM usage/cost tracking

---

## Roadmap

### Foundation

* [x] Agent runtime
* [x] Tool calling
* [x] Skill registry
* [x] Persistent sessions
* [x] Semantic memory
* [x] RAG knowledge ingestion
* [x] Qdrant integration
* [x] Multiple LLM providers
* [x] Streaming chat
* [x] FastAPI API
* [x] API-key authentication
* [x] Rate limiting
* [x] Request IDs
* [x] Health endpoints
* [x] Docker support
* [x] CI

### Production hardening

* [ ] Distributed Redis rate limiting
* [ ] Production migration workflow
* [ ] Provider connectivity checks
* [ ] External-service retry/backoff
* [ ] PostgreSQL-first production configuration
* [ ] Structured JSON logging
* [ ] OpenTelemetry tracing
* [ ] Dependency vulnerability scanning
* [ ] Comprehensive API integration tests
* [ ] Docker deployment smoke tests

### AI platform

* [ ] Local embedding support through Ollama
* [ ] Additional document loaders
* [ ] MCP integration
* [ ] Plugin lifecycle
* [ ] Per-agent permissions
* [ ] Agent configuration API
* [ ] Multi-agent orchestration
* [ ] Planning and reflection
* [ ] Agent evaluation framework

### SaaS

* [ ] User accounts
* [ ] Per-user API keys
* [ ] API key hashing
* [ ] Permissions/scopes
* [ ] Usage tracking
* [ ] Token/cost tracking
* [ ] Quotas
* [ ] Billing integration
* [ ] Web dashboard
* [ ] SDKs

---

## Design Principles

Doitall follows several principles:

### Provider independence

Applications should not be tightly coupled to one LLM provider.

### Explicit boundaries

Agents, providers, memory, tools, API, and persistence should remain independently replaceable.

### Safe defaults

Dangerous filesystem operations and production-unsafe configurations should be disabled or rejected by default.

### Persistence

Conversation and knowledge state should survive application restarts.

### Production awareness

Features should be designed with observability, security, failure handling, and deployment in mind.

---

## Contributing

Contributions are welcome.

Before submitting a pull request:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
```

For significant architectural changes, include:

* Problem statement
* Design decision
* Testing performed
* Operational impact
* Security considerations

---

## License

Apache-2.0

---

## Author

**Rohan Sharma**

GitHub:

https://github.com/RohanSharma-exe

---

## Star the Project

If Doitall is useful to you, consider giving the repository a ⭐.

It helps the project gain visibility and encourages further development.
