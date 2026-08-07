# Dockerfile for AI Business OS
# Multi-stage build: keeps the final image small and clean

# ── Stage 1: Builder ──────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install build tools needed to compile numpy from source
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY README.md ./

# Force numpy to build from source (no pre-built AVX2 wheels)
RUN pip install numpy==1.26.4 --no-binary numpy
RUN uv sync --frozen --no-dev

# ── Stage 2: Runtime ──────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /usr/local/lib/python3.11/site-packages/numpy /app/.venv/lib/python3.11/site-packages/numpy

# Copy source code and data
COPY src/ ./src/
COPY data/ ./data/

# Make sure venv binaries are used
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]