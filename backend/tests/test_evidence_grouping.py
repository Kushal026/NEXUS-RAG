"""
Tests for Claim-Centric Evidence Grouping and Conflict Analysis (Phase 6).
"""
import pytest
from app.infrastructure.evidence.claim_grouper import ClaimEvidenceGrouper
from app.domain.models import DocumentChunk, ScoredChunk


def test_claim_evidence_grouping_with_contradiction():
    grouper = ClaimEvidenceGrouper()

    claim = "Model X achieves 91% accuracy."

    # Chunk 1: Supports
    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="Our experiments demonstrate that Model X achieves 91% accuracy across validation sets.",
        span={"start_char": 0, "end_char": 90, "page_number": 4},
        metadata={"filename": "paper_primary.pdf"}
    )
    sc1 = ScoredChunk(chunk=c1, final_score=0.92)

    # Chunk 2: Contradicts (87%)
    c2 = DocumentChunk(
        id="c2",
        document_id="doc2",
        chunk_index=0,
        content="Independent tests revealed that Model X achieves 87% accuracy under identical evaluation.",
        span={"start_char": 0, "end_char": 90, "page_number": 2},
        metadata={"filename": "benchmark_audit.pdf"}
    )
    sc2 = ScoredChunk(chunk=c2, final_score=0.88)

    grouped = grouper.group_evidence_for_claims([claim], [sc1, sc2])
    assert len(grouped) == 1
    g = grouped[0]

    assert g.statement == claim
    assert len(g.supporting_citations) >= 1
    assert len(g.contradicting_citations) >= 1
    assert g.has_conflict is True
    assert g.conflict_explanation is not None
    assert "87%" in g.conflict_explanation or "CONTRADICTION" in g.conflict_explanation


def test_atomic_claim_extraction():
    grouper = ClaimEvidenceGrouper()
    text = (
        "### Key Findings\n"
        "- Transformer models utilize self-attention mechanisms to capture long-range dependencies.\n"
        "- The system achieves 95.4% precision on standard information retrieval benchmarks.\n"
        "- Fine-tuning requires 4 Nvidia A100 GPUs."
    )
    claims = grouper.extract_atomic_claims(text)
    assert len(claims) >= 2
    assert any("self-attention" in c for c in claims)
    assert any("95.4%" in c for c in claims)
