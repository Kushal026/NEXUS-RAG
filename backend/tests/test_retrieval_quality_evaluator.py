"""
Tests for Retrieval Quality Evaluator in Phase 7 Self-Correction.
"""
import pytest
from app.infrastructure.self_correction.retrieval_quality_evaluator import RetrievalQualityEvaluator
from app.domain.models import DocumentChunk, ScoredChunk, SelfCorrectionDecision


def test_high_quality_evidence_decision():
    evaluator = RetrievalQualityEvaluator()
    query = "Explain Transformer multi-head self-attention mechanism."

    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="The Transformer architecture relies entirely on multi-head self-attention mechanisms to compute representations.",
        span={"start_char": 0, "end_char": 100, "page_number": 1},
        metadata={"filename": "transformer_paper.pdf", "author": "Vaswani"}
    )
    sc1 = ScoredChunk(chunk=c1, final_score=0.92)

    quality = evaluator.evaluate_quality(query, [sc1])
    assert quality.overall_quality >= 0.60
    assert quality.recommended_decision == SelfCorrectionDecision.GENERATE
    assert quality.coverage_score > 0.60


def test_missing_gaps_triggers_retry():
    evaluator = RetrievalQualityEvaluator()
    query = "Explain quantum annealing and cryogenic thermal thresholds in supercomputers."

    # Chunk only discusses general quantum computing without cryogenic thresholds
    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="General overview of quantum computing and basic qubit registers.",
        span={"start_char": 0, "end_char": 60, "page_number": 1},
        metadata={"filename": "intro_quantum.txt"}
    )
    sc1 = ScoredChunk(chunk=c1, final_score=0.45)

    quality = evaluator.evaluate_quality(query, [sc1])
    assert len(quality.missing_gaps) > 0
    assert "cryogenic" in [g.lower() for g in quality.missing_gaps] or "thresholds" in [g.lower() for g in quality.missing_gaps]
    assert quality.recommended_decision == SelfCorrectionDecision.RETRY_MISSING_EVIDENCE


def test_contradictions_triggers_disambiguation():
    evaluator = RetrievalQualityEvaluator()
    query = "What is the accuracy of Model X?"

    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="Model X accuracy is 91% on benchmark tests.",
        span={"start_char": 0, "end_char": 50, "page_number": 1},
        metadata={"filename": "report_a.pdf"}
    )
    c2 = DocumentChunk(
        id="c2",
        document_id="doc2",
        chunk_index=0,
        content="Model X accuracy is 87% on benchmark tests.",
        span={"start_char": 0, "end_char": 50, "page_number": 1},
        metadata={"filename": "report_b.pdf"}
    )

    quality = evaluator.evaluate_quality(query, [ScoredChunk(chunk=c1, final_score=0.85), ScoredChunk(chunk=c2, final_score=0.82)])
    assert quality.has_contradictions is True
    assert quality.recommended_decision == SelfCorrectionDecision.RETRY_RESOLVE_CONTRADICTION
