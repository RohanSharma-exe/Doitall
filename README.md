# 🚀 Doitall

> A production-first AI framework for building intelligent agents, RAG systems, memory, knowledge bases, and AI-powered applications.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Tests](https://img.shields.io/badge/Tests-60%20Passing-success)
![Code%20Style](https://img.shields.io/badge/Ruff-Clean-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

---

# Vision

Doitall is an open-source framework designed to make building AI applications simple, modular, and production-ready.

Instead of focusing only on LLM calls, Doitall provides the infrastructure required for real-world AI systems:

* 🤖 Agents
* 🧠 Long-term Memory
* 📚 Knowledge Bases (RAG)
* 🔎 Semantic Search
* ⚡ Vector Databases
* 🔌 Multiple AI Providers
* 🛠 Tool Calling
* 💬 Conversations
* 📄 Document Ingestion
* 🚀 Extensible Architecture

---

# Current Features

## Agent System

* Agent model
* Agent manager
* Default agent factory

---

## Memory System

* Memory manager
* In-memory storage
* Vector memory storage
* Qdrant integration
* Semantic search
* Memory serialization

---

## Knowledge System

* Documents
* Chunking
* Knowledge repository
* Recursive directory loading
* TXT loader
* Markdown loader
* Loader registry
* Knowledge ingestion pipeline

---

## Embeddings

* Embedding manager
* LiteLLM integration
* Batch embeddings
* Provider abstraction

---

## Parsers

* Parser abstraction
* Text parser

---

## Serialization

* Memory serializer
* Chunk serializer

---

## Testing

Current project health:

* ✅ 60 Passing Tests
* ✅ Ruff Clean
* ✅ Modular Architecture
* ✅ Repository Pattern
* ✅ SOLID Principles
* ✅ Dependency Injection
* ✅ Clean Separation of Concerns

---

# Architecture

```text
                    Agent
                      │
                      ▼
               Conversation
                      │
                      ▼
               Prompt Builder
                      │
                      ▼
                 AI Runtime
          ┌──────────┴──────────┐
          ▼                     ▼
      Memory                Knowledge
          ▼                     ▼
   Vector Repository     Vector Repository
          ▼                     ▼
      Vector Store         Vector Store
          ▼                     ▼
          Qdrant / Future Providers
```

---

# Project Structure

```text
src/doitall/

├── agent/
├── api/
├── core/
├── embeddings/
├── knowledge/
├── memory/
├── models/
├── parsers/
├── providers/
├── runtime/
├── serialization/
├── tools/
└── utils/
```

---

# Tech Stack

* Python 3.14
* Pydantic v2
* LiteLLM
* Qdrant
* Ruff
* Pytest

---

# Roadmap

### ✅ Completed

* Agent Foundation
* Memory System
* Knowledge System
* Loader Registry
* Parser Layer
* Embeddings
* Vector Repository
* Semantic Search
* Repository Architecture

### 🚧 In Progress

* Prompt Builder
* Conversation Runtime
* Context Assembly
* Tool Execution Engine

### 📌 Planned

* PDF Loader
* HTML Loader
* DOCX Loader
* GitHub Loader
* Website Loader
* Streaming Responses
* Multi-Agent Support
* Workflow Engine
* MCP Integration
* Observability
* Evaluation Framework

---

# Development

Run formatting:

```bash
uv run ruff format .
```

Run linting:

```bash
uv run ruff check .
```

Run tests:

```bash
uv run pytest
```

---

# Philosophy

> Build infrastructure once. Build AI applications forever.

The goal of Doitall is to provide a clean, scalable foundation for production AI systems instead of one-off demos.

---

# Contributing

Contributions, ideas, and discussions are welcome.

If you're interested in AI agents, RAG, LLM infrastructure, or production AI engineering, feel free to open an issue or submit a pull request.

---

## ⭐ Star the repository if you find it useful!
