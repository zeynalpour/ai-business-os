# Contributing to AI Business OS

Thank you for your interest. Contributions of all kinds are welcome.

## How to add a new LLM Provider

1. Create `src/llm/your_provider.py`
2. Implement the `LLMProvider` Protocol (see `src/core/interfaces.py`)
3. Add your provider name to `config.py` and `main.py`
4. Add a test in `tests/`

No changes to core runtime needed. That's the whole point.

## How to add a new Gateway

1. Create `src/gateways/your_gateway.py`
2. Implement the `Gateway` Protocol (see `src/core/interfaces.py`)
3. Wire it in `main.py`

## Setup

```bash
git clone https://github.com/zeynalpour/ai-business-os.git
cd ai-business-os
uv sync --extra dev
cp .env.example .env
# fill in your keys
uv run python src/main.py
```

## Code standards

- Type hints everywhere
- Run `ruff check src/` before committing
- Run `mypy src/` before committing
- Add tests for new providers and gateways