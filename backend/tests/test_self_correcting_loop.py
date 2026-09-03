"""
Tests for Full Self-Correcting RAG Loop Execution and Termination Guard (Phase 7).
"""
import pytest
from unittest.mock import MagicMock
from app.services.self_correcting_service import SelfCorrectingService
from app.domain.models import DocumentChunk, ScoredChunk


def test_self_correcting_loop_execution_first_pass():
    # Setup mock retrieval service with high quality chunk
    mock_retrieval = MagicMock()
    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="The Transformer architecture relies on multi-head attention mechanisms to process sequence representations.",
        span={"start_char": 0, "end_char": 110, "page_number": 1},
        metadata={"filename": "transformer.pdf", "author": "Vaswani"}
    )
    mock_retrieval.retrieve_with_trace.return_value = ([ScoredChunk(chunk=c1, final_score=0.92)], None)

    service = SelfCorrectingService(retrieval_service=mock_retrieval, max_iterations=3)
    query = "What is the Transformer architecture and attention mechanism?"

    result = service.execute_self_correcting_rag(query=query)

    assert result.total_iterations == 1
    assert result.status == "first_pass_success"
    assert result.is_abstained is False
    assert len(result.accumulated_chunks) >= 1
    assert result.final_evidence_coverage >= 50.0


def test_self_correcting_loop_recovery_on_iteration_two():
    # Setup mock retrieval service: low quality on iter 1, high quality on iter 2
    mock_retrieval = MagicMock()
    c_low = DocumentChunk(
        id="c_low",
        document_id="doc_low",
        chunk_index=0,
        content="General introduction to computers and machines.",
        span={"start_char": 0, "end_char": 45, "page_number": 1},
        metadata={"filename": "intro.txt"}
    )
    c_good = DocumentChunk(
        id="c_good",
        document_id="doc_good",
        chunk_index=0,
        content="Cryogenic thermal thresholds for supercomputing systems operate below 4 Kelvin.",
        span={"start_char": 0, "end_char": 80, "page_number": 1},
        metadata={"filename": "cryo_specs.pdf"}
    )

    mock_retrieval.retrieve_with_trace.side_effect = [
        ([ScoredChunk(chunk=c_low, final_score=0.40)], None),   # Iteration 1
        ([ScoredChunk(chunk=c_good, final_score=0.90)], None),  # Iteration 2
    ]

    service = SelfCorrectingService(retrieval_service=mock_retrieval, max_iterations=3)
    query = "Explain cryogenic thermal thresholds in supercomputers."

    result = service.execute_self_correcting_rag(query=query)

    assert result.total_iterations == 2
    assert result.status == "recovered"
    assert result.is_abstained is False
    assert len(result.accumulated_chunks) == 2  # Accumulated both chunks!
    assert result.iterations_trace[1].rewrite_strategy is not None


def test_self_correcting_loop_abstention_on_empty_vault():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve_with_trace.return_value = ([], None)

    service = SelfCorrectingService(retrieval_service=mock_retrieval, max_iterations=2)
    query = "XyloQubitSuperQuantumNonexistent123456789"

    result = service.execute_self_correcting_rag(query=query, max_iterations=2)

    assert result.total_iterations <= 2
    assert result.is_abstained is True
    assert result.status == "abstained"
    assert "Insufficient Evidence" in result.final_answer_markdown

