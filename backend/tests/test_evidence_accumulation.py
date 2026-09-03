"""
Tests for Cross-Iteration Evidence Accumulator in Phase 7 Self-Correction.
"""
import pytest
from app.infrastructure.self_correction.evidence_accumulator import EvidenceAccumulator
from app.domain.models import DocumentChunk, ScoredChunk


def test_evidence_accumulation_and_score_update():
    accumulator = EvidenceAccumulator()

    c1 = DocumentChunk(id="c1", document_id="d1", chunk_index=0, content="Initial pass chunk 1", span={"start_char": 0, "end_char": 20})
    c2 = DocumentChunk(id="c2", document_id="d1", chunk_index=1, content="Initial pass chunk 2", span={"start_char": 20, "end_char": 40})

    existing = [
        ScoredChunk(chunk=c1, final_score=0.70),
        ScoredChunk(chunk=c2, final_score=0.65),
    ]

    # Iteration 2 retrieves c2 with higher score, and new chunk c3
    c3 = DocumentChunk(id="c3", document_id="d2", chunk_index=0, content="Iteration 2 new chunk", span={"start_char": 0, "end_char": 20})
    new_chunks = [
        ScoredChunk(chunk=c2, final_score=0.88),  # Higher score
        ScoredChunk(chunk=c3, final_score=0.92),  # New chunk
    ]

    accumulated = accumulator.accumulate(existing, new_chunks)

    assert len(accumulated) == 3
    # Top chunk should be c3 (0.92), then c2 (updated to 0.88), then c1 (0.70)
    assert accumulated[0].chunk.id == "c3"
    assert accumulated[1].chunk.id == "c2"
    assert accumulated[1].final_score == 0.88
    assert accumulated[2].chunk.id == "c1"
