"""Qdrant vector store for knowledge retrieval.

Stores and retrieves embedded knowledge chunks.
Collection names are namespaced by tenant_id, which is how
multi-tenancy works: one Qdrant instance, isolated collections.
"""

from __future__ import annotations

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from knowledge.chunker import Chunk
from knowledge.embedder import EMBEDDING_DIMENSION

logger = structlog.get_logger()


def _collection_name(tenant_id: str) -> str:
    """Namespace collections by tenant to support multi-tenancy."""
    return f"knowledge_{tenant_id}"


class VectorStore:
    """Qdrant-backed vector store for knowledge chunks."""

    def __init__(self, url: str = "http://localhost:6333") -> None:
        self._client = AsyncQdrantClient(url=url)

    async def ensure_collection(self, tenant_id: str) -> None:
        """Create collection if it doesn't exist."""
        name = _collection_name(tenant_id)
        exists = await self._client.collection_exists(name)

        if not exists:
            await self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("created collection", collection=name)

    async def upsert(
        self,
        tenant_id: str,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        """Store chunks and their embeddings."""
        name = _collection_name(tenant_id)

        points = [
            PointStruct(
                id=abs(hash(f"{chunk.source}:{chunk.chunk_index}")) % (2**63),
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "source": chunk.source,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata,
                },
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]

        await self._client.upsert(collection_name=name, points=points)
        logger.info("upserted chunks", collection=name, count=len(points))

    async def search(
        self,
        tenant_id: str,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[str]:
        """Search for relevant chunks and return their text."""
        name = _collection_name(tenant_id)

        results = await self._client.search(
            collection_name=name,
            query_vector=query_vector,
            limit=limit,
        )

        return [hit.payload["text"] for hit in results if hit.payload]