"""
Tests for Post-Generation Answer Verifier and Claim Filtering in Phase 7.
"""
import pytest
from app.infrastructure.self_correction.answer_verifier import AnswerVerifier
from app.domain.models import DocumentChunk, ScoredChunk


def test_answer_verification_filters_unsupported_claims():
    verifier = AnswerVerifier()

    # Draft answer contains 1 supported claim and 1 unsupported hallucinated claim
    draft_answer = (
        "### Key Architecture\n"
        "- The Transformer architecture relies on multi-head self-attention mechanisms.\n"
        "- The model was trained on 500 million quantum teleportation qubits."
    )

    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="The Transformer architecture relies on multi-head self-attention mechanisms for computing vector states.",
        span={"start_char": 0, "end_char": 100, "page_number": 1},
        metadata={"filename": "paper.pdf"}
    )
    accumulated = [ScoredChunk(chunk=c1, final_score=0.95)]

    result = verifier.verify_answer(draft_answer, accumulated)

    assert result.supported_claims_count == 1
    assert result.unsupported_claims_count == 1
    assert result.was_regenerated is True
    assert "self-attention" in result.final_answer
    assert "quantum teleportation" not in result.final_answer  # Redacted!
