"""Unit tests for RecursiveTextChunker."""

import pytest
from app.services.text_chunker import RecursiveTextChunker


def test_chunker_small_text_single_chunk() -> None:
    """Verify text smaller than chunk_size produces exactly one chunk."""
    chunker = RecursiveTextChunker(chunk_size=500, chunk_overlap=100)
    text = "Short sentence under 500 characters."
    chunks = chunker.split_text(text)
    assert len(chunks) == 1
    assert chunks[0].content == text
    assert chunks[0].index == 0


def test_chunker_splits_paragraphs_with_overlap() -> None:
    """Verify long text gets chunked with proper indexing and bounds."""
    chunker = RecursiveTextChunker(chunk_size=100, chunk_overlap=20)
    paragraphs = [
        "First long paragraph detailing the architectural principles of the Atlas AI system.",
        "Second paragraph explaining the pgvector indexing and cosine distance calculations.",
        "Third paragraph providing context on how embeddings are queried by similarity.",
    ]
    text = "\n\n".join(paragraphs)
    chunks = chunker.split_text(text)

    assert len(chunks) > 1
    for idx, c in enumerate(chunks):
        assert c.index == idx
        assert len(c.content) > 0


def test_chunker_invalid_overlap_raises() -> None:
    """Verify ValueError when overlap is greater than or equal to chunk size."""
    with pytest.raises(ValueError):
        RecursiveTextChunker(chunk_size=100, chunk_overlap=100)
