"""
Tests for Evidence Coverage and Safe Unknown Detection (Phase 6).
"""
import pytest
from app.infrastructure.evidence.coverage_evaluator import EvidenceCoverageEvaluator
from app.domain.models import GroupedClaimEvidence, ScoredChunk, DocumentChunk, SourceReliabilityScore


def test_high_evidence_coverage():
    evaluator = EvidenceCoverageEvaluator()

    claims = [
        GroupedClaimEvidence(statement="Claim 1", verification_status="supported"),
        GroupedClaimEvidence(statement="Claim 2", verification_status="supported"),
        GroupedClaimEvidence(statement="Claim 3", verification_status="supported"),
        GroupedClaimEvidence(statement="Claim 4", verification_status="insufficient_evidence"),
    ]

    c = DocumentChunk(id="c1", document_id="d1", chunk_index=0, content="High quality text", span={"start_char": 0, "end_char": 20})
    sc = ScoredChunk(chunk=c, final_score=0.85)

    source_scores = {
        "paper.pdf": SourceReliabilityScore(
            document_filename="paper.pdf",
            overall_score=0.90,
            source_type_score=0.95,
            authority_score=0.95,
            recency_score=0.90,
            corroboration_score=0.85,
            citation_quality_score=0.90,
            explanation="High quality"
        )
    }

    cov_pct, supp, contr, unsupp, is_unknown, reason, breakdown = evaluator.evaluate_coverage(
        grouped_claims=claims,
        retrieved_chunks=[sc],
        source_qualities=source_scores
    )

    assert cov_pct == 75.0  # 3 of 4 = 75%
    assert supp == 3
    assert unsupp == 1
    assert is_unknown is False
    assert breakdown.final_composite_score > 0.65


def test_insufficient_evidence_unknown_trigger():
    evaluator = EvidenceCoverageEvaluator()

    # Empty retrieved chunks or zero score
    claims = [GroupedClaimEvidence(statement="Unknown entity claim", verification_status="insufficient_evidence")]
    
    cov_pct, supp, contr, unsupp, is_unknown, reason, breakdown = evaluator.evaluate_coverage(
        grouped_claims=claims,
        retrieved_chunks=[],
        source_qualities={}
    )

    assert is_unknown is True
    assert reason is not None
    assert breakdown.final_composite_score == 0.0
