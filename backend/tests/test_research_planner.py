"""
Unit tests for Research Planner (Phase 9).
"""
import pytest
from app.infrastructure.agent.research_planner import ResearchPlanner


def test_research_planner_decomposition():
    planner = ResearchPlanner()
    goal = "Analyze current approaches to detecting deepfakes and compare their performance."

    plan = planner.generate_plan(goal)

    assert plan.goal == goal
    assert len(plan.sub_questions) >= 3
    # Check that analytical dimensions are covered
    sub_q_texts = " ".join([sq.question.lower() for sq in plan.sub_questions])
    assert "foundational" in sub_q_texts or "core" in sub_q_texts
    assert "models" in sub_q_texts or "methodologies" in sub_q_texts
    assert "performance" in sub_q_texts or "benchmarks" in sub_q_texts
    assert len(plan.key_hypotheses) >= 1
    assert "hybrid" in plan.strategy_overview.lower()
