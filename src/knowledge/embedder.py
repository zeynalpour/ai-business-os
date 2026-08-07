"""Embedding generator for knowledge ingestion pipeline.

Converts text chunks into vector embeddings using the configured
embedding model. Uses Google's text-embedding-004 via Metis/AvalAI
which gives 768-dimensional embeddings — good quality, low cost.
Embedder for AI Business OS — Metis native embeddings API."""

from __future__ import annotations

import httpx
import structlog

from knowledge.chunker import Chunk

logger = structlog.get_logger()

EMBEDDING_DIMENSION = 768 # text-embedding-004 dimension


class Embedder:
    """Generates embeddings for text chunks."""

    def __init__(
        self,
        api_key: str,
        base_url: str,  # from config
        model_family: str = "google",
        model_name: str = "text-embedding-004",
        proxy_url: str | None = None,
    ) -> None:
        self._url = base_url
        self._model = {"name": model_family, "model": model_name}
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self._proxy_url = proxy_url

    def _make_client(self) -> httpx.AsyncClient:
        if self._proxy_url:
            transport = httpx.AsyncHTTPTransport(proxy=self._proxy_url)
            return httpx.AsyncClient(transport=transport, timeout=30)
        return httpx.AsyncClient(timeout=30)

    async def embed(self, chunks: list[Chunk]) -> list[list[float]]:
        """Generate embeddings for a list of chunks.

        NOTE: Currently sends one request per chunk due to Metis API
        returning inconsistent batch sizes. This is a known limitation.
        TODO: Implement true batch embedding when switching to a provider
        with reliable batch support (OpenAI, Cohere, Jina direct API).
        Tracking issue: #XX
        """
        texts = [chunk.text for chunk in chunks]
        logger.info("embedding chunks", count=len(chunks))
        embeddings: list[list[float]] = []

        async with self._make_client() as client:
            for i, text in enumerate(texts):
                logger.debug("embedding chunk", index=i)
                response = await client.post(
                    self._url,
                    headers=self._headers,
                    json={"model": self._model, "input": text},
                )
                response.raise_for_status()
                data = response.json()
                embeddings.append(data["data"][0]["embedding"])

        return embeddings

    async def embed_query(self, query: str) -> list[float]:
        async with self._make_client() as client:
            response = await client.post(
                self._url,
                headers=self._headers,
                json={"model": self._model, "input": query},
            )
            response.raise_for_status()

        data = response.json()
        return data["data"][0]["embedding"]  # type: ignore[no-any-return]