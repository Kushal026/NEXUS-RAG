"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "NEXUS-RAG"


def test_system_status():
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "project_name" in data
    assert data["status"] == "operational"


def test_document_upload_and_query_flow():
    # 1. Upload sample document
    sample_content = (
        "# Quantum Computing and Neural Networks\n\n"
        "Quantum superposition allows qubits to represent multiple states simultaneously.\n"
        "In contrast, neural network weights adjust through gradient descent."
    )
    
    files = {
        "file": ("quantum_notes.md", sample_content.encode("utf-8"), "text/markdown")
    }

    upload_res = client.post("/api/v1/documents/upload", files=files)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    doc_id = upload_data["document_id"]
    assert upload_data["status"] == "indexed"
    assert upload_data["chunk_count"] >= 1

    # 2. List documents
    list_res = client.get("/api/v1/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert any(d["id"] == doc_id for d in docs)

    # 3. Inspect chunks
    chunks_res = client.get(f"/api/v1/documents/{doc_id}/chunks")
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    assert len(chunks) >= 1

    # 4. Search query
    search_payload = {
        "query": "quantum superposition qubits",
        "use_dense": True,
        "use_sparse": True,
        "use_reranker": True,
        "top_k": 5
    }
    search_res = client.post("/api/v1/query/search", json=search_payload)
    assert search_res.status_code == 200
    search_data = search_res.json()
    results = search_data["results"] if isinstance(search_data, dict) and "results" in search_data else search_data
    assert len(results) >= 1
    assert "superposition" in results[0]["chunk"]["content"].lower()
    if isinstance(search_data, dict) and "trace" in search_data:
        assert search_data["trace"]["query"] == "quantum superposition qubits"

    # 5. Full Evidence Synthesis
    synth_res = client.post("/api/v1/query/synthesize", json=search_payload)
    assert synth_res.status_code == 200
    synth_data = synth_res.json()
    assert "synthesis_markdown" in synth_data
    assert len(synth_data["claims"]) >= 1
    assert synth_data["overall_confidence"] > 0

    # 6. Delete document
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"
