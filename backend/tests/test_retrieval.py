"""
Unit tests for Dense Vector Store, BM25 Keyword Store, Hybrid Fusion, and Reranking.
"""
from app.domain.models import DocumentChunk, ChunkSpan, ScoredChunk
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.infrastructure.retrieval.fusion import HybridFusion
from app.infrastructure.retrieval.reranker import HeuristicReranker
import tempfile
from pathlib import Path


def create_mock_chunk(cid: str, text: str, emb: list) -> DocumentChunk:
    return DocumentChunk(
        id=cid,
        document_id="doc_1",
        chunk_index=0,
        content=text,
        span=ChunkSpan(start_char=0, end_char=len(text)),
        embedding=emb,
        metadata={"filename": "test.txt"}
    )


def test_bm25_keyword_store():
    store = BM25KeywordStore()
    c1 = create_mock_chunk("c1", "Quantum computing uses qubits and entanglement", [])
    c2 = create_mock_chunk("c2", "Deep learning utilizes backpropagation and neural layers", [])
    c3 = create_mock_chunk("c3", "Classical algorithms run on standard CPU architectures", [])

    store.index_chunks([c1, c2, c3])
    
    results = store.search("quantum entanglement", top_k=2)
    assert len(results) >= 1
    assert results[0].chunk.id == "c1"
    assert results[0].sparse_score > 0


def test_dense_vector_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "vecs.json"
        store = DenseVectorStore(storage_path=store_path)

        c1 = create_mock_chunk("c1", "Vector A", [1.0, 0.0, 0.0])
        c2 = create_mock_chunk("c2", "Vector B", [0.0, 1.0, 0.0])
        store.add_chunks([c1, c2])

        # Query aligned with c1
        results = store.search(query_vector=[0.9, 0.1, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0].chunk.id == "c1"
        assert results[0].dense_score > results[1].dense_score


def test_reciprocal_rank_fusion():
    c1 = create_mock_chunk("c1", "Chunk 1", [])
    c2 = create_mock_chunk("c2", "Chunk 2", [])

    dense_res = [
        ScoredChunk(chunk=c1, dense_score=0.9, dense_rank=1),
        ScoredChunk(chunk=c2, dense_score=0.6, dense_rank=2)
    ]
    sparse_res = [
        ScoredChunk(chunk=c2, sparse_score=0.95, sparse_rank=1),
        ScoredChunk(chunk=c1, sparse_score=0.3, sparse_rank=2)
    ]

    fused = HybridFusion.reciprocal_rank_fusion(
        dense_results=dense_res,
        sparse_results=sparse_res,
        dense_weight=0.5,
        sparse_weight=0.5,
        top_k=2
    )

    assert len(fused) == 2
    assert fused[0].rrf_score is not None


def test_heuristic_reranker():
    c1 = create_mock_chunk("c1", "The transformer architecture uses self-attention mechanisms.", [])
    c2 = create_mock_chunk("c2", "Weather forecast predicts rain tomorrow morning.", [])

    scored = [
        ScoredChunk(chunk=c2, final_score=0.5),
        ScoredChunk(chunk=c1, final_score=0.5)
    ]

    reranker = HeuristicReranker()
    reranked = reranker.rerank(query="transformer self-attention", scored_chunks=scored, top_k=2)

    assert reranked[0].chunk.id == "c1"
