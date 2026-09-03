"""
Tests for Entity Resolution and Deduplication (Phase 5).
Verifies canonicalization of variations like "OpenAI", "OpenAI Inc.", "OpenAI, Inc.".
"""
import pytest
from app.infrastructure.graph.entity_resolver import EntityResolver
from app.domain.models import EntityType, GraphProvenance


def test_entity_resolution_deduplication():
    resolver = EntityResolver()

    prov1 = GraphProvenance(
        document_id="doc1",
        document_filename="doc1.pdf",
        chunk_id="chunk1",
        page_number=1,
        exact_snippet="OpenAI is an AI research company.",
        confidence=0.95
    )

    prov2 = GraphProvenance(
        document_id="doc2",
        document_filename="doc2.pdf",
        chunk_id="chunk2",
        page_number=3,
        exact_snippet="OpenAI Inc. released GPT-4.",
        confidence=0.95
    )

    prov3 = GraphProvenance(
        document_id="doc3",
        document_filename="doc3.pdf",
        chunk_id="chunk3",
        page_number=5,
        exact_snippet="OpenAI, Inc. partnered with Microsoft.",
        confidence=0.95
    )

    # Resolve three variations of OpenAI
    node1 = resolver.resolve_entity("OpenAI", EntityType.COMPANY, prov1)
    node2 = resolver.resolve_entity("OpenAI Inc.", EntityType.COMPANY, prov2)
    node3 = resolver.resolve_entity("OpenAI, Inc.", EntityType.COMPANY, prov3)

    # All three mentions must resolve to the EXACT same canonical node ID and name
    assert node1.id == node2.id == node3.id
    assert node1.canonical_name == "OpenAI"
    assert node2.canonical_name == "OpenAI"
    assert node3.canonical_name == "OpenAI"

    # Mention count must be incremented to 3
    assert node1.mention_count == 3

    # All aliases must be recorded
    assert "OpenAI Inc." in node1.aliases or "OpenAI, Inc." in node1.aliases

    # All 3 provenance records must be accumulated
    assert len(node1.provenance_list) == 3
    doc_filenames = [p.document_filename for p in node1.provenance_list]
    assert "doc1.pdf" in doc_filenames
    assert "doc2.pdf" in doc_filenames
    assert "doc3.pdf" in doc_filenames


def test_distinct_entities_not_merged():
    resolver = EntityResolver()

    openai_node = resolver.resolve_entity("OpenAI", EntityType.COMPANY)
    google_node = resolver.resolve_entity("Google", EntityType.COMPANY)
    deepmind_node = resolver.resolve_entity("DeepMind", EntityType.COMPANY)

    assert openai_node.id != google_node.id
    assert openai_node.id != deepmind_node.id
    assert openai_node.canonical_name == "OpenAI"
    assert google_node.canonical_name == "Google"
