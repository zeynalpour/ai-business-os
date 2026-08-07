"""Text chunker for knowledge ingestion pipeline.

Splits raw text into overlapping chunks suitable for embedding.
Simple character-based chunking for v0.2 — can be upgraded to
semantic chunking in later phases without changing the interface.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """A single piece of text ready for embedding."""

    text: str
    source: str
    chunk_index: int
    metadata: dict[str, str]


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 50,
    metadata: dict[str, str] | None = None,
) -> list[Chunk]:
    """Split text into overlapping chunks.

    Args:
        text: Raw text to split
        source: Source identifier (filename, URL, etc.)
        chunk_size: Max characters per chunk
        overlap: Characters to overlap between chunks
        metadata: Extra metadata to attach to each chunk

    Returns:
        List of Chunk objects ready for embedding
    """
    if not text.strip():
        return []

    meta = metadata or {}
    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a paragraph or sentence boundary
        if end < len(text):
            for boundary in ["\n\n", "\n", ". ", " "]:
                pos = text.rfind(boundary, start, end)
                if pos != -1:
                    end = pos + len(boundary)
                    break

        chunk_text_content = text[start:end].strip()
        if chunk_text_content:
            chunks.append(
                Chunk(
                    text=chunk_text_content,
                    source=source,
                    chunk_index=index,
                    metadata={"source": source, "chunk_index": str(index), **meta},
                )
            )
            index += 1

        start = end - overlap

    return chunks