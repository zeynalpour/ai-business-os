"""Knowledge ingestion pipeline for AI Business OS.

Reads source files, chunks them, embeds them, and stores them
in the vector database. Run this script whenever knowledge changes.

Usage:
    uv run python src/knowledge/ingestion.py --tenant default --source data/demo_store/
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import structlog

from core.config import get_settings
from knowledge.chunker import chunk_text
from knowledge.embedder import Embedder
from knowledge.vector_store import VectorStore

logger = structlog.get_logger()


async def ingest_file(
    path: Path,
    tenant_id: str,
    embedder: Embedder,
    store: VectorStore,
    chunk_size: int,
    overlap: int,
) -> None:
    """Ingest a single markdown or text file."""
    logger.info("ingesting file", path=str(path))
    text = path.read_text(encoding="utf-8")

    chunks = chunk_text(
        text=text,
        source=str(path),
        chunk_size=chunk_size,
        overlap=overlap,
        metadata={"tenant_id": tenant_id, "filename": path.name},
    )

    if not chunks:
        logger.warning("no chunks produced", path=str(path))
        return

    embeddings = await embedder.embed(chunks)
    await store.upsert(tenant_id=tenant_id, chunks=chunks, embeddings=embeddings)
    logger.info("ingested file", path=str(path), chunks=len(chunks))


async def ingest_directory(
    source_dir: Path,
    tenant_id: str,
    embedder: Embedder,
    store: VectorStore,
    chunk_size: int,
    overlap: int,
) -> None:
    """Ingest all .md and .txt files in a directory."""
    files = list(source_dir.glob("**/*.md")) + list(source_dir.glob("**/*.txt"))

    if not files:
        logger.warning("no files found", directory=str(source_dir))
        return

    await store.ensure_collection(tenant_id)

    for file in files:
        await ingest_file(
            path=file,
            tenant_id=tenant_id,
            embedder=embedder,
            store=store,
            chunk_size=chunk_size,
            overlap=overlap,
        )

    logger.info("ingestion complete", files=len(files), tenant_id=tenant_id)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest knowledge into vector store")
    parser.add_argument("--tenant", default="default", help="Tenant ID")
    parser.add_argument("--source", default="data/demo_store/", help="Source directory")
    args = parser.parse_args()

    settings = get_settings()

    embedder = Embedder(
        api_key=settings.metis_api_key,
        base_url=settings.embedding_base_url,
        model_family="google",
        model_name=settings.embedding_model,
        proxy_url=settings.proxy_url,
    )

    store = VectorStore(url=settings.qdrant_url)

    await ingest_directory(
        source_dir=Path(args.source),
        tenant_id=args.tenant,
        embedder=embedder,
        store=store,
        chunk_size=settings.knowledge_chunk_size,
        overlap=settings.knowledge_chunk_overlap,
    )


if __name__ == "__main__":
    asyncio.run(main())