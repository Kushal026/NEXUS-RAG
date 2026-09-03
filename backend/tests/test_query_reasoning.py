"""
Unit tests for Query Reasoning Engine: Classification, Decomposition, Planning, Rewriting, and Multi-Hop Execution.
"""
from app.domain.models import QueryCategory
from app.infrastructure.query_reasoning.query_classifier import QueryClassifier
from app.infrastructure.query_reasoning.query_decomposer import QueryDecomposer
from app.infrastructure.query_reasoning.retrieval_planner import RetrievalPlanner
from app.infrastructure.query_reasoning.query_rewriter import QueryRewriter
from app.services.query_reasoning_service import QueryReasoningService


def test_query_classification():
    classifier = QueryClassifier()

    # Simple factual
    assert classifier.classify("What is the operating temperature of NEXUS-7700-TX?") == QueryCategory.SIMPLE_FACTUAL

    # Comparative
    assert classifier.classify("Compare dense vector search versus sparse BM25 retrieval") == QueryCategory.COMPARATIVE

    # Temporal
    assert classifier.classify("What was the timeline and history of HTTP RFC specifications after 2020?") == QueryCategory.TEMPORAL

    # Multi-hop
    multi_hop_q = "What techniques are introduced in paper X, who proposed them, and how did later papers evaluate them?"
    assert classifier.classify(multi_hop_q) == QueryCategory.MULTI_HOP


def test_query_decomposition():
    decomposer = QueryDecomposer()
    query = "What architecture is used in NEXUS-7700-TX, who designed it, and how is cryogenic temperature controlled?"
    steps = decomposer.decompose(query)

    assert len(steps) >= 2
    assert steps[0].step_number == 1
    assert steps[1].step_number == 2
    assert steps[1].depends_on_step == 1


def test_retrieval_planner():
    planner = RetrievalPlanner()
    
    # Simple query generates 1-step direct plan
    simple_plan = planner.create_plan("What is RFC-9110?")
    assert simple_plan.estimated_hops == 1
    assert not simple_plan.is_multihop

    # Multi-hop query generates multi-step plan
    complex_q = "What algorithms are in NEXUS-7700-TX, who created them, and how do they perform?"
    multi_plan = planner.create_plan(complex_q)
    assert multi_plan.is_multihop
    assert len(multi_plan.steps) >= 2


def test_query_rewriter():
    rewriter = QueryRewriter()

    # Rewrite for low confidence
    rewritten, strategy = rewriter.rewrite_for_low_confidence("What are the techniques?", 0.25)
    assert "methods" in rewritten or "technical specifications" in rewritten

    # Context injection
    injected = rewriter.inject_intermediate_context(
        sub_query="how is temperature maintained?",
        prior_facts=["NEXUS-7700-TX controller operating conditions"],
        prior_entities=["NEXUS-7700-TX"]
    )
    assert "NEXUS-7700-TX" in injected


def test_multihop_reasoning_execution():
    service = QueryReasoningService()
    
    # Single hop execution
    res_single = service.execute_reasoning_pipeline("What is RFC-9110?")
    assert res_single.multihop_trace is not None
    assert res_single.multihop_trace.total_hops_executed == 1
    assert res_single.multihop_trace.stop_reason == "single_hop_direct"

    # Multi hop execution
    complex_q = "What techniques are used in NEXUS-7700-TX, who operates it, and how is cryogenic coherence maintained?"
    res_multi = service.execute_reasoning_pipeline(complex_q)
    assert res_multi.multihop_trace is not None
    assert len(res_multi.multihop_trace.step_evidences) >= 2
    assert res_multi.multihop_trace.stop_reason in ("plan_completed", "max_hops_reached")
