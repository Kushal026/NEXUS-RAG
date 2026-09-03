"""
Evaluation API endpoints: Trigger automated benchmarks and retrieve quantitative IR metrics.
"""
from fastapi import APIRouter, HTTPException
from app.domain.models import BenchmarkReport
from app.evaluation.benchmark import RetrievalBenchmarkRunner
from app.core.logging import logger

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarking"])


@router.post("/run", response_model=BenchmarkReport)
async def run_retrieval_benchmark():
    """Runs a standard multi-method IR benchmark (Pure Vector vs Pure BM25 vs Hybrid RRF vs Hybrid+Reranker)."""
    try:
        runner = RetrievalBenchmarkRunner()
        report = runner.run_benchmark()
        return report
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")
