"""
Tests for Multi-Factor Source Reliability Engine (Phase 6).
"""
import pytest
from app.infrastructure.evidence.source_reliability_evaluator import SourceReliabilityEvaluator


def test_source_reliability_academic_vs_notes():
    evaluator = SourceReliabilityEvaluator()

    # Academic Paper with Author and Top Organization
    score_academic = evaluator.evaluate_source(
        document_filename="attention_is_all_you_need_neurips.pdf",
        chunk_content="Authored by Vaswani et al. at Google Research in 2023.",
        document_metadata={"author": "Ashish Vaswani", "page_count": 15},
        corroboration_count=3
    )

    # Informal Unstructured Notes
    score_notes = evaluator.evaluate_source(
        document_filename="scratch_notes.txt",
        chunk_content="Quick notes on some models.",
        document_metadata={},
        corroboration_count=1
    )

    assert score_academic.overall_score > score_notes.overall_score
    assert score_academic.source_type_score >= 0.90
    assert score_academic.authority_score >= 0.90
    assert score_academic.corroboration_score >= 0.90
    assert "×" in score_academic.explanation or "%" in score_academic.explanation


def test_corroboration_factor_boost():
    evaluator = SourceReliabilityEvaluator()

    score_single = evaluator.evaluate_source(
        document_filename="benchmark.pdf",
        chunk_content="GLUE score 91%.",
        corroboration_count=1
    )

    score_corroborated = evaluator.evaluate_source(
        document_filename="benchmark.pdf",
        chunk_content="GLUE score 91%.",
        corroboration_count=3
    )

    assert score_corroborated.corroboration_score > score_single.corroboration_score
    assert score_corroborated.overall_score > score_single.overall_score
