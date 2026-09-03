"""
Tests for Phase 6 Evidence Intelligence REST Endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_pairwise_nli_api_endpoint():
    payload = {
        "premise": "Model accuracy is 91% on GLUE.",
        "hypothesis": "Model accuracy is 87% on SQuAD."
    }
    res = client.post("/api/v1/evidence/nli", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] == "different_conditions"
    assert data["confidence"] >= 0.8
    assert "GLUE" in (data["condition_a"] or "") or "GLUE" in data["explanation"]


def test_source_quality_api_endpoint():
    payload = {
        "filename": "quantum_deep_learning.pdf",
        "content": "Published by Google DeepMind researchers in 2024 with full author affiliations."
    }
    res = client.post("/api/v1/evidence/source-quality", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["overall_score"] > 0.7
    assert data["document_type"] == "academic_paper"


def test_evidence_analyze_api_endpoint():
    payload = {
        "query": "What is Transformer model architecture and accuracy?",
        "top_k": 5
    }
    res = client.post("/api/v1/evidence/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "evidence_coverage_percentage" in data
    assert "composite_evidence_score" in data
    assert "synthesis_markdown" in data
    assert "grouped_claims" in data
