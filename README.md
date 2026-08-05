# AI Business OS

**The open-source platform for autonomous AI employees.**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> Businesses should not say *"I need a chatbot."*
> They should say *"I need an AI Sales Employee."*
>
> AI Business OS is the runtime that powers those employees.

---

## What is this?

AI Business OS is a production-grade, open-source platform for creating,
deploying, and managing autonomous AI employees for real businesses.

This is **not**:
- another chatbot wrapper
- another RAG demo
- another LangChain project

This **is**:
- a clean, modular AI runtime built on real software engineering principles
- a reference architecture for production Agentic AI
- an educational resource for AI/LLM engineers
- a platform designed to grow to 100+ contributors

---

## Architecture

```
Telegram · WhatsApp · Slack · Discord · REST
                     │
                     ▼
          Conversation Gateway
                     │
                     ▼
        Conversation Orchestrator
                     │
                     ▼
            Agent Runtime
                     │
          ┌──────────┴──────────┐
        LLM Provider        (Phase 2+)
      OpenAI · Gemini      Memory · RAG
      Grok · Ollama         Tools · MCP
```

The runtime never knows which gateway, LLM, or tool provider is active.
Everything communicates through interfaces.

---

## Quickstart

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An API key from [Metis](https://metisai.ir) or [AvalAI](https://avalai.ir)

### Run in 3 steps

**1. Clone and install**
```bash
git clone https://github.com/zeynalpour/ai-business-os.git
cd ai-business-os
uv sync
```

**2. Configure**
```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

**3. Start**
```bash
uv run python src/main.py
```

Open Telegram, find your bot, and send a message. You now have a working
AI Sales Employee.

---

## Supported LLM Providers

| Provider | Models | Notes |
|----------|--------|-------|
| [Metis](https://metisai.ir) | gemini-2.5-flash-lite, gpt-4o-mini, grok-beta | Recommended for Iran |
| [AvalAI](https://avalai.ir) | gemini-2.0-flash, gpt-4o | OpenAI-compatible |

Switch providers by changing `LLM_PROVIDER` in your `.env` — no code changes needed.

---

## Project Structure

```
src/
  core/         # Interfaces, models, config — the heart of the platform
  gateways/     # Channel adapters (Telegram, REST, ...)
  llm/          # LLM provider implementations
  runtime/      # Agent runtime (Sales Employee, ...)
tests/          # Test suite
docs/           # Architecture docs, ADRs, server setup
examples/       # Runnable examples
```

---

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 0 — Foundation | ✅ Done | Architecture, interfaces, CI/CD |
| 1 — AI Runtime | ✅ Done | Telegram + LLM + Agent working end-to-end |
| 2 — Knowledge | 🔜 Next | RAG, embeddings, vector database |
| 3 — Memory | ⬜ Planned | User memory, business memory |
| 4 — Tools | ⬜ Planned | MCP, Composio, native tools |
| 5 — Multi-Agent | ⬜ Planned | Planner, specialized agents |
| 6 — Production | ⬜ Planned | Dashboard, observability, metrics |
| 7 — Ecosystem | ⬜ Planned | SDK, plugins, marketplace |

---

## Contributing

Contributions are welcome. The architecture is designed so you can add a
new gateway, LLM provider, or tool without touching the core runtime.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.

Good first issues are labeled
[![good first issue](https://img.shields.io/github/issues/zeynalpour/ai-business-os/good%20first%20issue)](https://github.com/zeynalpour/ai-business-os/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

---

## Design Principles

- **Interface First** — everything depends on abstractions, never concretions
- **Async First** — the entire platform is asynchronous
- **Event Driven** — every interaction is a normalized event
- **Provider Agnostic** — swap any LLM, gateway, or database in one line
- **Modular** — add a new integration without touching core business logic

---

## License

MIT — see [LICENSE](LICENSE)

---

<p align="center">
  Built to become the strongest open-source AI engineering portfolio project.
</p>
`