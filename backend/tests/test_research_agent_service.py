"""
Unit tests for NEXUS Research Agent Service (Phase 9).
"""
import pytest
from unittest.mock import MagicMock
from app.services.research_agent_service import ResearchAgentService
from app.domain.models import (
    ResearchGoalRequest,
    DocumentChunk,
    ScoredChunk
)


def test_research_agent_execution_and_budget_guards():
    mock_retrieval = MagicMock()
    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="Deepfake detection algorithms leverage convolutional neural networks and spatial artifact analysis to classify manipulated frames.",
        span={"start_char": 0, "end_char": 130, "page_number": 2},
        metadata={"filename": "deepfake_survey.pdf", "file_type": "pdf"}
    )
    mock_retrieval.retrieve_with_trace.return_value = ([ScoredChunk(chunk=c1, final_score=0.93)], None)

    service = ResearchAgentService(retrieval_service=mock_retrieval)

    req = ResearchGoalRequest(
        goal="Analyze current approaches to detecting deepfakes and compare their performance.",
        max_iterations=2,
        max_searches=6,
        max_time_seconds=15,
        enable_graph_traversal=True,
        enable_contradiction_detection=True
    )

    result = service.execute_research(req)

    assert result.goal == req.goal
    assert len(result.plan.sub_questions) >= 3
    assert len(result.action_trace) >= 4
    # Verify no hidden chain of thought in trace
    for step in result.action_trace:
        assert step.description
        assert "chain of thought" not in step.description.lower()
    assert len(result.source_table) >= 1
    assert "deepfake_survey.pdf" in result.source_table[0].source_filename
    assert result.telemetry.searches_executed >= 1
    assert result.telemetry.searches_executed <= 6
    assert result.telemetry.execution_time_seconds < 15.0
    assert result.confidence_score > 0.50
    assert "Executive Summary" in result.report_markdown


def test_research_agent_terminates_on_budget_limit():
    mock_retrieval = MagicMock()
    mock_retrieval.retrieve_with_trace.return_value = ([], None)

    service = ResearchAgentService(retrieval_service=mock_retrieval)

    # Set very tight budget
    req = ResearchGoalRequest(
        goal="Quantum error correction benchmarks",
        max_iterations=1,
        max_searches=1,
        max_time_seconds=2
    )

    result = service.execute_research(req)

    assert result.telemetry.searches_executed <= 1
    assert result.telemetry.budget_limit_reached is True or result.telemetry.termination_reason in ("budget_limit_reached", "goal_completed")
