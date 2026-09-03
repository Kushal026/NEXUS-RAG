"""
Integration tests for FastAPI Research Agent Endpoints (Phase 9).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_agent_plan_api():
    response = client.post(
        "/api/v1/agent/plan",
        json={"goal": "Analyze current approaches to detecting deepfakes and compare their performance."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "plan_id" in data
    assert "sub_questions" in data
    assert len(data["sub_questions"]) >= 3
    assert "strategy_overview" in data


def test_agent_research_api():
    response = client.post(
        "/api/v1/agent/research",
        json={
            "goal": "Overview of Transformer attention mechanisms and benchmarks.",
            "max_iterations": 2,
            "max_searches": 4,
            "max_time_seconds": 15,
            "enable_graph_traversal": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert "report_markdown" in data
    assert "source_table" in data
    assert "action_trace" in data
    assert "telemetry" in data
    assert data["telemetry"]["searches_executed"] >= 1
