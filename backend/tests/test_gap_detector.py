"""
Unit tests for Gap Detector (Phase 9).
"""
import pytest
from app.infrastructure.agent.gap_detector import GapDetector
from app.domain.models import ResearchPlan, ResearchSubQuestion, DocumentChunk, ScoredChunk


def test_gap_detector_identifies_missing_areas():
    detector = GapDetector()

    plan = ResearchPlan(
        goal="Transformer benchmark analysis",
        sub_questions=[
            ResearchSubQuestion(
                id="sq1",
                question="What are the foundational architectures and attention mechanisms?",
                priority=1,
                status="pending"
            ),
            ResearchSubQuestion(
                id="sq2",
                question="What are the cryogenic thermal benchmarks in supercomputers?",
                priority=2,
                status="pending"
            )
        ],
        identified_entities=["Transformer", "Attention"],
        key_hypotheses=["Transformers scale efficiently"]
    )

    # Evidence only contains transformer text, no cryogenic text
    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="The Transformer architecture uses multi-head self-attention mechanisms to process sequence tokens.",
        span={"start_char": 0, "end_char": 100, "page_number": 1},
        metadata={"filename": "transformer.pdf"}
    )
    chunks = [ScoredChunk(chunk=c1, final_score=0.92)]

    follow_ups, updated_sqs = detector.evaluate_plan_gaps(plan, chunks)

    assert len(updated_sqs) == 2
    assert updated_sqs[0].status == "answered"
    assert updated_sqs[1].status == "partial_gap"
    assert len(follow_ups) >= 1
    assert "cryogenic" in follow_ups[0].lower() or "thermal" in follow_ups[0].lower()
