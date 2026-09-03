"""
Unit tests for Advanced Hybrid Retrieval, Metadata Filtering, and Observability Tracing.
"""
from app.domain.models import DocumentChunk, ChunkSpan, RetrievalMode
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.services.retrieval_service import RetrievalService
from pathlib import Path
import tempfile


def test_metadata_filtering_and_trace():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_store = DenseVectorStore(storage_path=Path(tmpdir) / "vecs.json")
        k_store = BM25KeywordStore()
        service = RetrievalService(vector_store=v_store, keyword_store=k_store)

        c1_text = "RFC-9110 specifies HTTP semantics and status codes"
        c2_text = "Quantum algorithms utilize Hadamard gates and superposition"

        embs = service.embedder.embed_texts([c1_text, c2_text])

        c1 = DocumentChunk(
            id="c1",
            document_id="d1",
            chunk_index=0,
            content=c1_text,
            span=ChunkSpan(start_char=0, end_char=50),
            embedding=embs[0],
            metadata={"filename": "rfc9110.pdf", "file_type": "pdf", "author": "Fielding"}
        )
        c2 = DocumentChunk(
            id="c2",
            document_id="d2",
            chunk_index=0,
            content=c2_text,
            span=ChunkSpan(start_char=0, end_char=60),
            embedding=embs[1],
            metadata={"filename": "quantum.md", "file_type": "md", "author": "Shor"}
        )

        v_store.add_chunks([c1, c2])
        k_store.index_chunks([c1, c2])

        # 1. Filter by author Fielding
        results, trace = service.retrieve_with_trace(
            query="HTTP protocols",
            mode=RetrievalMode(metadata_filter={"author": "Fielding"}, top_k=5)
        )
        assert len(results) == 1
        assert results[0].chunk.id == "c1"

        # 2. Verify Observability Trace
        assert trace.query == "HTTP protocols"
        assert trace.query_analysis is not None
        assert trace.vector_candidates_count >= 1
        assert "vector_search_ms" in trace.stage_latencies_ms
        assert "fusion_ms" in trace.stage_latencies_ms
