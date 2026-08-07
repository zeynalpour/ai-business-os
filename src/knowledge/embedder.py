"""Embedding generator for knowledge ingestion pipeline.

Converts text chunks into vector embeddings using the configured
embedding model. Uses Google's text-embedding-004 via Metis/AvalAI
which gives 768-dimensional embeddings — good quality, low cost.
"""

from __future__ import annotations

import structlog
from google import genai
from google.genai import types

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
        MODEL = {"name": model_family, "model": model_name}
        self._model = MODEL

        import os
        if proxy_url:
            os.environ["HTTPS_PROXY"] = proxy_url
            os.environ["HTTP_PROXY"] = proxy_url

        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(base_url=base_url),
        )

    async def embed(self, chunks: list[Chunk]) -> list[list[float]]:
        """Generate embeddings for a list of chunks.

        Returns list of embedding vectors in the same order as input.
        """
        embeddings = []

        for chunk in chunks:
            logger.debug("embedding chunk", 
                         source=chunk.source, 
                         index=chunk.chunk_index
                        )
            result = await self._client.aio.models.embed_content(
                model=self._model,
                contents=chunk.text,
            )
            embeddings.append(result.embeddings[0].values)

        return embeddings

    async def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query string."""
        result = await self._client.aio.models.embed_content(
            model=self._model,
            contents=query,
        )
        return result.embeddings[0].values