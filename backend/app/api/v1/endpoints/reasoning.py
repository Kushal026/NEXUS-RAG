"""
Reasoning API endpoints: Planning, multi-hop retrieval execution, and reasoning benchmarks.
"""
from typing import Dict, Any, List, Optional
import time
from fastapi import APIRouter, Depends, HTTPException
from app.domain.models import RetrievalPlan, EvidenceSynthesisResult
from app.schemas.requests import QueryRequest
from app.services.query_reasoning_service import QueryReasoningService
from app.core.logging import logger

router = APIRouter(prefix="/reasoning", tags=["Query Reasoning & Planning Engine"])

_reasoning_service: Optional[QueryReasoningService] = None


def get_reasoning_service() -> QueryReasoningService:
    global _reasoning_service
    if _reasoning_service is None:
        _reasoning_service = QueryReasoningService()
    return _reasoning_service


@router.post("/plan", response_model=RetrievalPlan)
async def generate_retrieval_plan(
    req: QueryRequest,
    service: QueryReasoningService = Depends(get_reasoning_service)
):
    """Classifies query and generates an atomic multi-step or single-step execution plan."""
    try:
        return service.generate_plan(req.query)
    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@router.post("/multihop", response_model=EvidenceSynthesisResult)
async def execute_multihop_reasoning(
    req: QueryRequest,
    service: QueryReasoningService = Depends(get_reasoning_service)
):
    """Executes multi-hop iterative retrieval reasoning with intermediate fact extraction and safety guardrails."""
    try:
        return service.execute_reasoning_pipeline(query=req.query)
    except Exception as e:
        logger.error(f"Multi-hop reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-hop execution failed: {str(e)}")


@router.post("/benchmark")
async def run_reasoning_benchmark(
    service: QueryReasoningService = Depends(get_reasoning_service)
):
    """Executes comparative benchmark comparing Simple Queries vs Multi-Hop Complex Queries."""
    test_suite = [
        {
            "type": "simple_factual",
            "query": "What is the operating temperature of NEXUS-7700-TX controller?",
            "is_multihop_expected": False
        },
        {
            "type": "simple_standard",
            "query": "RFC-9110 HTTP semantics specification",
            "is_multihop_expected": False
        },
        {
            "type": "multi_hop_compound",
            "query": "What techniques are used in NEXUS-7700-TX, who operates it, and how is cryogenic coherence maintained?",
            "is_multihop_expected": True
        },
        {
            "type": "comparative_research",
            "query": "Compare dense semantic vectors versus sparse BM25 retrieval and explain how neural reranking evaluates them",
            "is_multihop_expected": True
        }
    ]

    results = []
    for item in test_suite:
        t0 = time.time()
        plan = service.generate_plan(item["query"])
        res = service.execute_reasoning_pipeline(item["query"])
        elapsed = round((time.time() - t0) * 1000, 2)
        
        hops = len(res.multihop_trace.step_evidences) if res.multihop_trace else 1
        results.append({
            "query": item["query"],
            "type": item["type"],
            "planned_hops": len(plan.steps),
            "executed_hops": hops,
            "latency_ms": elapsed,
            "accumulated_chunks_count": len(res.multihop_trace.all_accumulated_chunks) if res.multihop_trace else len(res.retrieved_chunks),
            "confidence": res.overall_confidence
        })

    return {
        "status": "success",
        "benchmark_timestamp": time.time(),
        "queries_evaluated": len(results),
        "results": results
    }
