"""
Tests for Entity Extraction Engine with Strict Provenance (Phase 5).
"""
import pytest
from app.infrastructure.graph.entity_extractor import EntityExtractor
from app.domain.models import DocumentChunk, EntityType


def test_entity_extraction_types_and_spans():
    extractor = EntityExtractor()
    sample_text = (
        'The paper "Attention Is All You Need" was written by Ashish Vaswani and Noam Shazeer '
        'at Google DeepMind in 2017. It introduced the Transformer architecture, which was later '
        'used by OpenAI to build GPT-4 and evaluated on the SQuAD and GLUE benchmarks.'
    )

    chunk = DocumentChunk(
        id="chunk-test-01",
        document_id="doc-transformer-paper",
        chunk_index=0,
        content=sample_text,
        span={"start_char": 0, "end_char": len(sample_text), "page_number": 1, "section_title": "Introduction"},
        metadata={"filename": "attention_paper.pdf"}
    )

    extractions = extractor.extract_from_chunk(chunk)
    assert len(extractions) > 0

    extracted_names = [e[0] for e in extractions]
    extracted_types = {e[0]: e[1] for e in extractions}

    # Verify key entities detected
    assert any("Attention Is All You Need" in name for name in extracted_names)
    assert "Ashish Vaswani" in extracted_names
    assert "Noam Shazeer" in extracted_names
    assert any("Google" in name or "DeepMind" in name for name in extracted_names)
    assert "Transformer" in extracted_names
    assert "GPT-4" in extracted_names
    assert "OpenAI" in extracted_names
    assert "GLUE" in extracted_names or "SQuAD" in extracted_names

    # Check Taxonomy Type assignments
    assert extracted_types["Ashish Vaswani"] == EntityType.PERSON
    assert extracted_types["GPT-4"] == EntityType.MODEL
    assert extracted_types["Transformer"] == EntityType.TECHNOLOGY

    # Verify Provenance retention
    for raw_name, ent_type, prov in extractions:
        assert prov.document_id == "doc-transformer-paper"
        assert prov.document_filename == "attention_paper.pdf"
        assert prov.chunk_id == "chunk-test-01"
        assert prov.page_number == 1
        assert len(prov.exact_snippet) > 0
        assert prov.confidence >= 0.7


def test_adhoc_text_extraction():
    extractor = EntityExtractor()
    text = "Sam Altman is the CEO of OpenAI, which created ChatGPT and GPT-4o."
    extractions = extractor.extract_from_text(text)
    names = [e[0] for e in extractions]

    assert "Sam Altman" in names
    assert "OpenAI" in names
    assert "ChatGPT" in names or "GPT-4o" in names
