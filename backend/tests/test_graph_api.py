"""
Tests for Phase 5 Knowledge Graph REST Endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_graph_stats_and_schema_endpoints():
    res_stats = client.get("/api/v1/graph/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "total_entities" in stats
    assert "total_relationships" in stats
    assert "storage_engine" in stats

    res_schema = client.get("/api/v1/graph/schema")
    assert res_schema.status_code == 200
    schema = res_schema.json()
    assert "entity_types" in schema
    assert "relationship_types" in schema
    assert "model" in schema["entity_types"]
    assert "AUTHORED_BY" in schema["relationship_types"]


def test_graph_extract_endpoint():
    payload = {
        "text": "Vaswani et al. authored Attention Is All You Need at Google in 2017, introducing Transformer."
    }
    res = client.post("/api/v1/graph/extract", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "entities" in data
    assert "relationships" in data
    assert len(data["entities"]) > 0


def test_graph_entities_and_neighborhood_endpoints():
    # Trigger ad-hoc extraction first or query entities
    res_entities = client.get("/api/v1/graph/entities")
    assert res_entities.status_code == 200
    entities = res_entities.json()
    assert isinstance(entities, list)

    if len(entities) > 0:
        target_id = entities[0]["id"]
        res_entity = client.get(f"/api/v1/graph/entities/{target_id}")
        assert res_entity.status_code == 200
        assert res_entity.json()["id"] == target_id

        res_neigh = client.get(f"/api/v1/graph/neighborhood/{target_id}?depth=1")
        assert res_neigh.status_code == 200
        assert "nodes" in res_neigh.json()
        assert "edges" in res_neigh.json()


def test_hybrid_graph_rag_endpoint():
    payload = {
        "query": "What is Transformer and who authored it?",
        "top_k": 5,
        "max_graph_hops": 2
    }
    res = client.post("/api/v1/graph/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "synthesis_markdown" in data
    assert "claims" in data
    assert "graph_entities" in data
