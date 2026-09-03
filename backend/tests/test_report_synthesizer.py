"""
Unit tests for Report Synthesizer (Phase 9).
"""
import pytest
from app.infrastructure.agent.report_synthesizer import ReportSynthesizer
from app.domain.models import (
    ResearchPlan,
    ResearchSubQuestion,
    DocumentChunk,
    ScoredChunk
)


def test_report_synthesizer_compiles_9_sections_and_source_table():
    synthesizer = ReportSynthesizer()

    goal = "Evaluate deepfake detection algorithms"
    plan = ResearchPlan(
        goal=goal,
        sub_questions=[
            ResearchSubQuestion(id="sq1", question="What models exist?", status="answered", key_findings_summary="CNN and ViT are widely used."),
            ResearchSubQuestion(id="sq2", question="What are the accuracy limits?", status="partial_gap", key_findings_summary="Cross-dataset drops.")
        ],
        identified_entities=["Deepfake", "ViT"],
        key_hypotheses=["ViT outperforms CNN on cross-dataset"]
    )

    c1 = DocumentChunk(
        id="c1",
        document_id="doc1",
        chunk_index=0,
        content="Deepfake detection via Vision Transformers achieves 92.4% accuracy on FaceForensics++.",
        span={"start_char": 0, "end_char": 85, "page_number": 4},
        metadata={"filename": "deepfake_vit.pdf", "file_type": "pdf", "author": "Zhang"}
    )
    chunks = [ScoredChunk(chunk=c1, final_score=0.91)]

    contradictions = [{
        "source_a": "Accuracy is 92.4%",
        "source_b": "Accuracy drops to 78.1% on unseen datasets",
        "explanation": "Different evaluation datasets"
    }]

    # 1. Build Source Table
    source_table = synthesizer.build_source_table(chunks)
    assert len(source_table) == 1
    assert source_table[0].source_filename == "deepfake_vit.pdf"
    assert source_table[0].source_type == "Academic Paper (Peer-Reviewed)"
    assert source_table[0].relevance_score == 0.91
    assert source_table[0].provenance_page == 4

    # 2. Synthesize Report
    report_md = synthesizer.synthesize_report(
        goal=goal,
        plan=plan,
        sub_questions=plan.sub_questions,
        accumulated_chunks=chunks,
        contradictions=contradictions,
        source_table=source_table
    )

    assert "Executive Summary" in report_md
    assert "Methodology & Retrieval Strategy" in report_md
    assert "Key Findings" in report_md
    assert "Comparative Analysis" in report_md
    assert "Conflicting Evidence" in report_md
    assert "⚠ Conflicting Evidence Detected" in report_md
    assert "Limitations & Information Gaps" in report_md
    assert "Conclusion" in report_md
    assert "Source & Evidence Table" in report_md
    assert "| `deepfake_vit.pdf` |" in report_md
    assert "Citations & Exact Provenance" in report_md
