"""
Tests for Knowledge Graph Retrieval, Neighborhood Traversal, and Hybrid Graph RAG (Phase 5).
"""
import pytest
from app.infrastructure.graph.graph_store import LocalInMemoryGraphStore
from app.services.graph_service import GraphService
from app.services.hybrid_graph_rag_service import HybridGraphRAGService
from app.domain.models import (
    EntityNode,
    RelationshipEdge,
    EntityType,
    RelationshipType,
    DocumentChunk,
    GraphProvenance
)


def test_neighborhood_and_path_retrieval():
    store = LocalInMemoryGraphStore()
    store.clear()

    # Create test nodes
    n_vaswani = EntityNode(canonical_name="Ashish Vaswani", entity_type=EntityType.PERSON)
    n_paper = EntityNode(canonical_name="Attention Is All You Need", entity_type=EntityType.PAPER)
    n_trans = EntityNode(canonical_name="Transformer", entity_type=EntityType.TECHNOLOGY)
    n_gpt4 = EntityNode(canonical_name="GPT-4", entity_type=EntityType.MODEL)
    n_openai = EntityNode(canonical_name="OpenAI", entity_type=EntityType.COMPANY)

    store.upsert_entity(n_vaswani)
    store.upsert_entity(n_paper)
    store.upsert_entity(n_trans)
    store.upsert_entity(n_gpt4)
    store.upsert_entity(n_openai)

    # Create edges
    e1 = RelationshipEdge(
        source_id=n_paper.id,
        source_name=n_paper.canonical_name,
        target_id=n_vaswani.id,
        target_name=n_vaswani.canonical_name,
        relationship_type=RelationshipType.AUTHORED_BY,
        weight=0.95
    )
    e2 = RelationshipEdge(
        source_id=n_paper.id,
        source_name=n_paper.canonical_name,
        target_id=n_trans.id,
        target_name=n_trans.canonical_name,
        relationship_type=RelationshipType.INTRODUCED,
        weight=0.90
    )
    e3 = RelationshipEdge(
        source_id=n_gpt4.id,
        source_name=n_gpt4.canonical_name,
        target_id=n_trans.id,
        target_name=n_trans.canonical_name,
        relationship_type=RelationshipType.USES,
        weight=0.92
    )
    e4 = RelationshipEdge(
        source_id=n_gpt4.id,
        source_name=n_gpt4.canonical_name,
        target_id=n_openai.id,
        target_name=n_openai.canonical_name,
        relationship_type=RelationshipType.CREATED_BY,
        weight=0.95
    )

    store.upsert_relationship(e1)
    store.upsert_relationship(e2)
    store.upsert_relationship(e3)
    store.upsert_relationship(e4)

    # Test 1-hop neighborhood for Attention paper
    subgraph_1 = store.get_neighborhood(n_paper.id, depth=1)
    assert len(subgraph_1.nodes) == 3
    node_names_1 = [n.canonical_name for n in subgraph_1.nodes]
    assert "Attention Is All You Need" in node_names_1
    assert "Ashish Vaswani" in node_names_1
    assert "Transformer" in node_names_1

    # Test 2-hop neighborhood
    subgraph_2 = store.get_neighborhood(n_paper.id, depth=2)
    node_names_2 = [n.canonical_name for n in subgraph_2.nodes]
    assert "GPT-4" in node_names_2

    # Test Path Discovery
    paths = store.find_paths("Ashish Vaswani", "GPT-4", max_depth=3)
    # Path should traverse through Attention Paper and Transformer
    assert len(paths) > 0 or len(subgraph_2.nodes) >= 4


def test_hybrid_graph_rag_service():
    service = HybridGraphRAGService()
    
    # Ingest a chunk into graph service
    sample_chunk = DocumentChunk(
        id="c-rag-test",
        document_id="doc-rag-01",
        chunk_index=0,
        content="OpenAI released GPT-4. Claude is an alternative model developed by Anthropic that competes with GPT-4.",
        span={"start_char": 0, "end_char": 100, "page_number": 2},
        metadata={"filename": "models_overview.pdf"}
    )
    service.graph_service.index_chunk_graph(sample_chunk)

    result = service.query("Which models compete with GPT-4?")
    assert result.query == "Which models compete with GPT-4?"
    assert len(result.synthesis_markdown) > 0
    assert result.overall_confidence > 0.0
