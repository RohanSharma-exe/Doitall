# Doitall Architecture

> **Status:** In Development
> **Version:** 0.1.0

## Overview

Doitall is a modular AI framework designed to build production-ready AI applications. It provides a provider-agnostic runtime, an extensible skill system, memory, knowledge retrieval, and agent execution while keeping each component independent and testable.

---

## High-Level Flow

```text
User
 │
 ▼
ChatService
 │
 ▼
ConversationService
 │
 ▼
ContextAssembler
 │
 ▼
RuntimeContext
 │
 ▼
Provider selection (default or per-request override)
 │
 ▼
AgentExecutor
 │
 ▼
RuntimeExecutor
 │
 ▼
Provider (Gemini, OpenAI, ...)
 │
 ▼
ProviderResponse
 │
 ▼
ToolCallingEngine
 │
 ▼
SkillManager
 │
 ▼
Skills
```

---

## Core Components

### Runtime

Responsible for building prompts and communicating with AI providers.

- RuntimeContext
- PromptBuilder
- RuntimeExecutor

---

### Agent

Coordinates the AI execution loop.

Responsibilities:

- Execute LLM requests
- Execute requested tools
- Continue until no tool calls remain

---

### Skills

Skills are executable capabilities exposed to the LLM.

Current examples:

- Calculator
- Filesystem

Each skill provides:

- Metadata (`ToolDefinition`)
- Execution logic

---

### Providers

Providers communicate with different LLM APIs.

Current:

- Gemini (LiteLLM)
- Groq (LiteLLM)
- OpenAI (LiteLLM)
- Anthropic (LiteLLM)
- Ollama (LiteLLM)
- OpenRouter (LiteLLM)

Future:

- Provider-specific health checks
- Streaming support
- Additional hosted/local providers

---

### Memory

Stores long-term information for conversations.

---

### Knowledge

Provides Retrieval-Augmented Generation (RAG) support.

Knowledge ingestion returns basic operational metadata:

- document ID
- indexed chunk count
- status

---

### Workspace

Provides secure access to local files and directories.

---

## Design Principles

- Provider-agnostic runtime
- Modular architecture
- Strong typing
- Dependency injection
- Test-driven development
- Small, focused components
- Easily extensible

---

## Current Status

### Completed

- Runtime
- Agent execution loop
- Tool execution
- Skill registry
- Provider abstraction
- Gemini provider
- Provider registry with configurable default provider
- Per-request provider override plumbing
- Memory system
- Knowledge system
- Knowledge ingestion API
- FastAPI routes for chat, health, providers, and knowledge ingestion
- Optional API key auth for mutating endpoints
- Workspace
- Dependency injection
- Comprehensive unit tests

### Metrics

- ✅ Unit test suite present
- ✅ Ruff Clean

---

## Implemented Features

The following items were previously listed as future work and are now complete:

- ✅ **Native tool calling** — `AgentExecutor` drives a bounded tool-calling loop (max 10 iterations)
- ✅ **Streaming responses** — `POST /v1/chat/stream` returns SSE events; client-disconnect detection added
- ✅ **Multiple tool execution** — the agent loop handles parallel and sequential tool calls per turn
- ✅ **Persisted conversation sessions** — SQLModel/SQLite backend; sessions survive restarts
- ✅ **Knowledge management CRUD** — `GET/DELETE /v1/knowledge`, `POST /v1/knowledge/search`

---

## Future Work

Genuinely not-yet-implemented items:

- **MCP support** — `mcp/` module is a stub; `POST /v1/extensions` returns 501 for `mcp_server` kind
- **Plugin support** — `plugins/` module is a stub; `POST /v1/extensions` returns 501 for `plugin` kind
- **Structured outputs** — provider structured-output mode not wired
- **Multi-agent orchestration** — single-agent execution only
- **Real provider health checks** — `GET /v1/health/providers` uses best-effort availability flags
- **Observability & tracing** — `/metrics` endpoint present but returns process-local counters only; Prometheus integration is Milestone 2
- **Production deployment guide** — `docs/Production-Readiness.md` has a checklist; no Helm/k8s manifests yet
- **Web frontend** — fully specified in `docs/product-requirements.md` and `docs/frontend-plan.md`; implementation is Milestone 2

---

This document is intentionally brief during development.

A complete architecture guide with detailed component diagrams, sequence diagrams, extension guides, and contributor documentation will be created before the first stable release.
