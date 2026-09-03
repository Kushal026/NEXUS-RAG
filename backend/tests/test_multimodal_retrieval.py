"""
Unit tests for Multimodal Retrieval Service & Strict Citation Provenance (Phase 8).
"""
import pytest
from unittest.mock import MagicMock
from app.services.multimodal_service import MultimodalService
from app.domain.models import DocumentChunk, ScoredChunk, ModalityType, Document, DocumentMetadata


def test_multimodal_document_representation_hierarchy():
    service = MultimodalService()
    doc_content = """
# Transformer Overview

Table 1: Hyperparameter Config
| Layers | Heads | d_model |
| 6 | 8 | 512 |
| 12 | 16 | 1024 |

Figure 2: Attention Architecture
Plots layer depth over training steps with 95% accuracy.

```python
def self_attention(q, k, v):
    return torch.bmm(q, k)
```

[1] Vaswani et al., Attention is All You Need, 2017.
"""
    doc = Document(
        filename="transformer_paper.md",
        content=doc_content,
        metadata=DocumentMetadata(
            title="Transformer Paper",
            file_type="markdown",
            file_size=len(doc_content),
            page_count=1
        )
    )

    repr_tree = service.build_document_representation(doc)

    assert repr_tree.filename == "transformer_paper.md"
    assert len(repr_tree.tables) == 1
    assert repr_tree.tables[0].num_rows == 2
    assert len(repr_tree.figures) == 1
    assert "Figure 2" in repr_tree.figures[0].caption
    assert len(repr_tree.code_blocks) == 1
    assert repr_tree.code_blocks[0].language == "python"
    assert len(repr_tree.references) >= 1


def test_multimodal_retrieval_and_provenance():
    mock_retrieval = MagicMock()
    chunk_table = DocumentChunk(
        id="c_tbl",
        document_id="doc_paper",
        chunk_index=0,
        content="Table 3: Results\n| Model | BLEU |\n| Trans | 28.4 |",
        span={"start_char": 0, "end_char": 50, "page_number": 12},
        metadata={"filename": "Paper.pdf"}
    )
    chunk_fig = DocumentChunk(
        id="c_fig",
        document_id="doc_paper",
        chunk_index=1,
        content="Figure 3: Latency curves across token lengths reaching 45ms.",
        span={"start_char": 51, "end_char": 120, "page_number": 12},
        metadata={"filename": "Paper.pdf"}
    )

    mock_retrieval.retrieve_with_trace.return_value = (
        [ScoredChunk(chunk=chunk_table, final_score=0.88), ScoredChunk(chunk=chunk_fig, final_score=0.85)],
        None
    )

    service = MultimodalService(retrieval_service=mock_retrieval)

    # 1. Retrieve across all modalities
    res = service.retrieve_multimodal_evidence(query="transformer benchmark table and latency figure")

    assert len(res.evidence_items) >= 2
    # Verify strict provenance label (e.g. Figure 3 • Paper.pdf • Page 12)
    prov_labels = [e.provenance_label for e in res.evidence_items]
    assert any("Paper.pdf" in p and "Page 12" in p for p in prov_labels)
    assert any(e.modality == ModalityType.TABLE for e in res.evidence_items)
    assert any(e.modality == ModalityType.FIGURE for e in res.evidence_items)

    # 2. Retrieve with filter
    res_tbl_only = service.retrieve_multimodal_evidence(query="benchmark", requested_modality="table")
    assert all(e.modality == ModalityType.TABLE for e in res_tbl_only.evidence_items)
