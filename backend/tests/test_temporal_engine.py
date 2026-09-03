"""
Unit tests for Temporal Knowledge Engine: Metadata Extraction, Filter Engine,
Conflict Resolution, Point-in-Time Retrieval, and Version Evolution.
"""
from app.domain.models import (
    DocumentChunk,
    ChunkSpan,
    TemporalFilter,
    TemporalConflictType,
    RetrievalMode
)
from app.infrastructure.temporal.temporal_extractor import TemporalExtractor
from app.infrastructure.temporal.temporal_filter import TemporalFilterEngine
from app.infrastructure.temporal.temporal_conflict_resolver import TemporalConflictResolver
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.services.retrieval_service import RetrievalService
from app.services.temporal_service import TemporalService
from pathlib import Path
import tempfile


def test_temporal_extractor():
    extractor = TemporalExtractor()

    # Point in time query
    f1, _ = extractor.extract_temporal_filter("What was the operating state as of 2023?")
    assert f1 is not None
    assert f1.as_of_date == "2023"

    # Date range query
    f2, _ = extractor.extract_temporal_filter("What changed between 2024 and 2026?")
    assert f2 is not None
    assert f2.start_date == "2024"
    assert f2.end_date == "2026"

    # Latest information query
    f3, _ = extractor.extract_temporal_filter("What is the latest specification of controller?")
    assert f3 is not None
    assert f3.latest_only is True

    # Version query
    f4, _ = extractor.extract_temporal_filter("Show me details for version 2.0.0")
    assert f4 is not None
    assert f4.version == "2.0.0"


def test_temporal_filter_engine():
    # Chunk from 2023 v1 (superseded)
    c_v1 = DocumentChunk(
        id="c1",
        document_id="d1",
        chunk_index=0,
        content="NEXUS controller operates at 100 millikelvin in 2023",
        span=ChunkSpan(start_char=0, end_char=50),
        version="1.0.0",
        is_latest=False,
        metadata={"valid_from": "2023-01-01", "valid_until": "2023-12-31", "is_latest": False, "version": "1.0.0"}
    )

    # Chunk from 2026 v3 (latest)
    c_v3 = DocumentChunk(
        id="c3",
        document_id="d3",
        chunk_index=0,
        content="NEXUS controller operates at 15 millikelvin in 2026",
        span=ChunkSpan(start_char=0, end_char=50),
        version="3.0.0",
        is_latest=True,
        metadata={"valid_from": "2026-01-01", "is_latest": True, "version": "3.0.0"}
    )

    # Test latest_only filter
    f_latest = TemporalFilter(latest_only=True)
    assert not TemporalFilterEngine.matches_chunk(c_v1, f_latest)
    assert TemporalFilterEngine.matches_chunk(c_v3, f_latest)

    # Test as_of 2023 filter
    f_2023 = TemporalFilter(as_of_date="2023")
    assert TemporalFilterEngine.matches_chunk(c_v1, f_2023)
    assert not TemporalFilterEngine.matches_chunk(c_v3, f_2023)


def test_temporal_conflict_resolver():
    resolver = TemporalConflictResolver()

    # 1. Version supersession
    res_v = resolver.resolve_conflict(
        claim_a="Operating temperature is 100mK",
        claim_b="Operating temperature is 15mK",
        doc_a="specs_v1.md",
        doc_b="specs_v2.md",
        version_a="1.0.0",
        version_b="2.0.0"
    )
    assert res_v.conflict_type == TemporalConflictType.VERSION_CHANGE
    assert "supersedes" in res_v.explanation

    # 2. Temporal Evolution
    res_evo = resolver.resolve_conflict(
        claim_a="Operating temperature is 100mK in 2023",
        claim_b="Operating temperature is 15mK in 2026",
        timestamp_a="2023",
        timestamp_b="2026"
    )
    assert res_evo.conflict_type == TemporalConflictType.TEMPORAL_EVOLUTION
    assert "evolved" in res_evo.explanation

    # 3. Genuine Contradiction
    res_contra = resolver.resolve_conflict(
        claim_a="Operating temperature is 100mK in 2026",
        claim_b="Operating temperature is 15mK in 2026",
        timestamp_a="2026",
        timestamp_b="2026"
    )
    assert res_contra.conflict_type == TemporalConflictType.GENUINE_CONTRADICTION


def test_temporal_retrieval_and_diff():
    with tempfile.TemporaryDirectory() as tmpdir:
        v_store = DenseVectorStore(storage_path=Path(tmpdir) / "temporal_vecs.json")
        k_store = BM25KeywordStore()
        retrieval_svc = RetrievalService(vector_store=v_store, keyword_store=k_store)

        c1_text = "NEXUS controller operates at 100 millikelvin in 2023"
        c2_text = "NEXUS controller operates at 15 millikelvin in 2026"
        embs = retrieval_svc.embedder.embed_texts([c1_text, c2_text])

        c1 = DocumentChunk(
            id="c1",
            document_id="d1",
            chunk_index=0,
            content=c1_text,
            span=ChunkSpan(start_char=0, end_char=50),
            embedding=embs[0],
            version="1.0.0",
            is_latest=False,
            metadata={"valid_from": "2023-01-01", "valid_until": "2023-12-31", "is_latest": False, "version": "1.0.0"}
        )
        c2 = DocumentChunk(
            id="c2",
            document_id="d2",
            chunk_index=0,
            content=c2_text,
            span=ChunkSpan(start_char=0, end_char=50),
            embedding=embs[1],
            version="2.0.0",
            is_latest=True,
            metadata={"valid_from": "2026-01-01", "is_latest": True, "version": "2.0.0"}
        )

        v_store.add_chunks([c1, c2])
        k_store.index_chunks([c1, c2])

        temporal_svc = TemporalService(retrieval_service=retrieval_svc)

        # 1. Point in time 2023 retrieval
        res_2023 = temporal_svc.query_as_of(query="operating temperature", as_of_date="2023")
        assert len(res_2023.retrieved_chunks) >= 1
        assert res_2023.retrieved_chunks[0].chunk.id == "c1"

        # 2. Latest retrieval
        res_latest, _ = retrieval_svc.retrieve_with_trace(
            query="operating temperature",
            mode=RetrievalMode(temporal_filter=TemporalFilter(latest_only=True))
        )
        assert len(res_latest) >= 1
        assert res_latest[0].chunk.id == "c2"

        # 3. Temporal diff between 2023 and 2026
        diff_res = temporal_svc.compare_temporal_diff(
            topic="operating temperature",
            period_from="2023",
            period_to="2026"
        )
        assert diff_res.period_from == "2023"
        assert diff_res.period_to == "2026"
        assert len(diff_res.detected_changes) >= 1
        assert diff_res.detected_changes[0].prior_state == "100 millikelvin"
        assert diff_res.detected_changes[0].current_state == "15 millikelvin"
