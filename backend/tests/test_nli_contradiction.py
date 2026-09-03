"""
Tests for Deterministic NLI & Contradiction Detection Engine (Phase 6).
"""
import pytest
from app.infrastructure.evidence.nli_engine import NLIEngine
from app.domain.models import NLIClassificationType


def test_direct_numerical_contradiction():
    engine = NLIEngine()
    # Direct contradiction: 91% vs 87% on same target
    statement_a = "Model accuracy is 91% on the test split."
    statement_b = "Model accuracy is 87% on the test split."

    res = engine.evaluate_pair(premise=statement_a, hypothesis=statement_b)
    assert res.verdict == NLIClassificationType.CONTRADICTION
    assert res.confidence >= 0.85
    assert "91%" in res.explanation and "87%" in res.explanation
    assert res.metric_diff is not None


def test_different_conditions_detection():
    engine = NLIEngine()
    # Different datasets/conditions: GLUE vs SQuAD
    statement_a = "Model achieved 91% accuracy on the GLUE benchmark."
    statement_b = "Model achieved 87% accuracy on the SQuAD dataset."

    res = engine.evaluate_pair(premise=statement_a, hypothesis=statement_b)
    assert res.verdict == NLIClassificationType.DIFFERENT_CONDITIONS
    assert "GLUE" in (res.condition_a or "") or "GLUE" in res.explanation
    assert "SQuAD" in (res.condition_b or "") or "SQuAD" in res.explanation


def test_temporal_difference_detection():
    engine = NLIEngine()
    # Temporal difference: 2022 vs 2024
    statement_a = "In 2022, system accuracy was measured at 85%."
    statement_b = "In 2024, system accuracy reached 93%."

    res = engine.evaluate_pair(premise=statement_a, hypothesis=statement_b)
    assert res.verdict == NLIClassificationType.TEMPORAL_DIFFERENCE
    assert res.confidence >= 0.85
    assert "2022" in res.explanation and "2024" in res.explanation


def test_mutual_entailment_agreement():
    engine = NLIEngine()
    statement_a = "The Transformer architecture relies on the multi-head self-attention mechanism."
    statement_b = "Self-attention mechanism with multiple heads is used in the Transformer architecture."

    res = engine.evaluate_pair(premise=statement_a, hypothesis=statement_b)
    assert res.verdict == NLIClassificationType.ENTAILMENT
    assert res.confidence >= 0.80


def test_polarity_negation_contradiction():
    engine = NLIEngine()
    statement_a = "Model X outperforms Model Y on language comprehension tasks."
    statement_b = "Model X fails and is inferior to Model Y on language comprehension tasks."

    res = engine.evaluate_pair(premise=statement_a, hypothesis=statement_b)
    assert res.verdict in (NLIClassificationType.CONTRADICTION, NLIClassificationType.PARTIAL_CONTRADICTION)
