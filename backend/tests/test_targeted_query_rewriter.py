"""
Tests for Targeted Query Rewriter in Phase 7 Self-Correction.
"""
import pytest
from app.infrastructure.self_correction.targeted_query_rewriter import TargetedQueryRewriter
from app.domain.models import SelfCorrectionDecision


def test_gap_targeting_rewrite():
    rewriter = TargetedQueryRewriter()
    query = "Explain supercomputing hardware."
    gaps = ["cryogenic", "thermal", "thresholds"]

    rewritten, strategy = rewriter.rewrite_query(
        original_query=query,
        decision=SelfCorrectionDecision.RETRY_MISSING_EVIDENCE,
        missing_gaps=gaps,
        iteration=2
    )

    assert strategy == "missing_gap_targeting"
    assert "cryogenic" in rewritten
    assert "supercomputing" in rewritten


def test_contradiction_disambiguation_rewrite():
    rewriter = TargetedQueryRewriter()
    query = "What is the accuracy of Transformer models?"

    rewritten, strategy = rewriter.rewrite_query(
        original_query=query,
        decision=SelfCorrectionDecision.RETRY_RESOLVE_CONTRADICTION,
        missing_gaps=[],
        iteration=2
    )

    assert strategy == "contradiction_disambiguation"
    assert "benchmark" in rewritten.lower() or "evaluation" in rewritten.lower()
