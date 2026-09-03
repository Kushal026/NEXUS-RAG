"""
Tests for Relationship Extraction with Strict Chunk Provenance (Phase 5).
"""
import pytest
from app.infrastructure.graph.entity_extractor import EntityExtractor
from app.infrastructure.graph.entity_resolver import EntityResolver
from app.infrastructure.graph.relationship_extractor import RelationshipExtractor
from app.domain.models import DocumentChunk, EntityType, RelationshipType


def test_relationship_extraction_with_provenance():
    extractor = EntityExtractor()
    resolver = EntityResolver()
    rel_extractor = RelationshipExtractor()

    text = (
        'The seminal paper "Attention Is All You Need" was authored by Ashish Vaswani. '
        'The work introduced the Transformer architecture, which was developed by researchers at Google DeepMind. '
        'Later, GPT-4 was created by OpenAI using the Transformer framework.'
    )

    chunk = DocumentChunk(
        id="chunk-rel-01",
        document_id="doc-research-ai",
        chunk_index=0,
        content=text,
        span={"start_char": 0, "end_char": len(text), "page_number": 7, "section_title": "Model Architecture"},
        metadata={"filename": "paper.pdf"}
    )

    raw_extractions = extractor.extract_from_chunk(chunk)
    resolved_entities = [resolver.resolve_entity(name, t, prov) for name, t, prov in raw_extractions]

    edges = rel_extractor.extract_relationships_from_chunk(chunk, resolved_entities)
    assert len(edges) > 0

    edge_tuples = [(e.source_name, e.relationship_type, e.target_name) for e in edges]

    # Verify key relationships
    assert any(
        "Attention Is All You Need" in src and rel == RelationshipType.AUTHORED_BY and "Ashish Vaswani" in tgt
        for src, rel, tgt in edge_tuples
    )
    assert any(
        "GPT-4" in src and rel == RelationshipType.CREATED_BY and "OpenAI" in tgt
        for src, rel, tgt in edge_tuples
    )

    # Verify Strict Provenance on each edge
    for edge in edges:
        assert len(edge.provenance_list) > 0
        prov = edge.provenance_list[0]
        assert prov.document_id == "doc-research-ai"
        assert prov.document_filename == "paper.pdf"
        assert prov.chunk_id == "chunk-rel-01"
        assert prov.page_number == 7
        assert len(prov.exact_snippet) > 0


def test_no_unsupported_relationships_hallucinated():
    rel_extractor = RelationshipExtractor()
    resolver = EntityResolver()

    # Two entities with unrelated sentence
    e1 = resolver.resolve_entity("ImageNet", EntityType.DATASET)
    e2 = resolver.resolve_entity("PyTorch", EntityType.TECHNOLOGY)

    chunk = DocumentChunk(
        id="unrelated-chunk",
        document_id="doc-unrelated",
        chunk_index=0,
        content="ImageNet is a vision dataset. Meanwhile, PyTorch is a library for tensors.",
        span={"start_char": 0, "end_char": 70}
    )

    edges = rel_extractor.extract_relationships_from_chunk(chunk, [e1, e2])
    # No direct relationship should be asserted
    assert len(edges) == 0
