"""
Tests for Self-Correction REST Endpoints in Phase 7.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_self_correcting_query_endpoint():
    payload = {
        "query": "Explain Transformer multi-head attention and RRF ranking.",
        "max_iterations": 2,
        "top_k": 5
    }
    res = client.post("/api/v1/self-correction/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "total_iterations" in data
    assert "iterations_trace" in data
    assert "final_answer_markdown" in data
    assert "status" in data


def test_evaluate_quality_endpoint():
    payload = {
        "query": "Explain Transformer self-attention.",
        "chunk_texts": [
            "The Transformer architecture utilizes self-attention mechanisms to relate positions of a sequence."
        ]
    }
    res = client.post("/api/v1/self-correction/evaluate-quality", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "overall_quality" in data
    assert "recommended_decision" in data
    assert data["recommended_decision"] in ("generate", "retry_missing_evidence")


def test_verify_answer_endpoint():
    payload = {
        "raw_answer": "Transformer uses self-attention mechanisms. It operates on 100 quantum entangled qubits.",
        "evidence_texts": [
            "Transformer uses self-attention mechanisms to process sequence representations."
        ]
    }
    res = client.post("/api/v1/self-correction/verify-answer", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "supported_claims_count" in data
    assert "unsupported_claims_count" in data
    assert data["supported_claims_count"] >= 1
