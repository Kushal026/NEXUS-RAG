"""
Unit tests for semantic chunking and span tracking.
"""
from app.domain.models import Document, DocumentMetadata
from app.infrastructure.chunking.semantic_chunker import SemanticChunker


def test_semantic_chunker_basic():
    doc = Document(
        filename="overview.txt",
        content="## Introduction\nArtificial Intelligence is transforming search engines.\n\n## Methodology\nHybrid retrieval combines dense and sparse search techniques.\n\n## Results\nAccuracy increases significantly.",
        metadata=DocumentMetadata(
            title="Overview",
            file_type="txt",
            file_size=150
        )
    )

    chunker = SemanticChunker(chunk_size=100, chunk_overlap=20, min_chunk_length=15)
    chunks = chunker.chunk(doc)

    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.document_id == doc.id
        assert chunk.span.start_char >= 0
        assert chunk.span.end_char > chunk.span.start_char
        assert chunk.metadata["filename"] == "overview.txt"


def test_chunker_page_marker_parsing():
    content = "<!-- PAGE_1 -->\nPage 1 content about neural graphs.\n\n<!-- PAGE_2 -->\nPage 2 content discussing rerankers."
    doc = Document(
        filename="paged.txt",
        content=content,
        metadata=DocumentMetadata(file_type="txt", file_size=len(content))
    )

    chunker = SemanticChunker(chunk_size=80, chunk_overlap=10, min_chunk_length=10)
    chunks = chunker.chunk(doc)

    assert len(chunks) >= 2
    page_numbers = [c.span.page_number for c in chunks]
    assert 1 in page_numbers or 2 in page_numbers
