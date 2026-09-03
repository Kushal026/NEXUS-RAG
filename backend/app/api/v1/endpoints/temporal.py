"""
Temporal API endpoints: Point-in-time queries, temporal diff comparisons, and conflict resolution.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.domain.models import (
    EvidenceSynthesisResult,
    TemporalDiffResult,
    TemporalConflictResult,
    TemporalFilter
)
from app.services.temporal_service import TemporalService
from app.core.logging import logger

router = APIRouter(prefix="/temporal", tags=["Temporal Knowledge Engine"])

_temporal_service: Optional[TemporalService] = None


def get_temporal_service() -> TemporalService:
    global _temporal_service
    if _temporal_service is None:
        _temporal_service = TemporalService()
    return _temporal_service


class TemporalQueryRequest(BaseModel):
    query: str
    as_of_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    version: Optional[str] = None
    latest_only: bool = False
    top_k: int = 5


class TemporalDiffRequest(BaseModel):
    topic: str
    period_from: str
    period_to: str


class ConflictCheckRequest(BaseModel):
    claim_a: str
    claim_b: str
    timestamp_a: Optional[str] = None
    timestamp_b: Optional[str] = None
    doc_a: Optional[str] = None
    doc_b: Optional[str] = None
    version_a: Optional[str] = None
    version_b: Optional[str] = None


@router.post("/query", response_model=EvidenceSynthesisResult)
async def temporal_query(
    req: TemporalQueryRequest,
    service: TemporalService = Depends(get_temporal_service)
):
    """Executes time-aware query with point-in-time or latest-version constraints."""
    try:
        if req.as_of_date:
            return service.query_as_of(query=req.query, as_of_date=req.as_of_date, top_k=req.top_k)
        
        t_filter = TemporalFilter(
            as_of_date=req.as_of_date,
            start_date=req.start_date,
            end_date=req.end_date,
            version=req.version,
            latest_only=req.latest_only
        )
        from app.domain.models import RetrievalMode
        mode = RetrievalMode(temporal_filter=t_filter, top_k=req.top_k * 2, rerank_top_k=req.top_k)
        chunks, trace = service.retrieval_service.retrieve_with_trace(query=req.query, mode=mode)
        synthesis = service.llm_provider.generate_synthesis(query=req.query, evidence_chunks=chunks)
        synthesis.retrieval_trace = trace
        return synthesis
    except Exception as e:
        logger.error(f"Temporal query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Temporal query failed: {str(e)}")


@router.post("/diff", response_model=TemporalDiffResult)
async def temporal_diff(
    req: TemporalDiffRequest,
    service: TemporalService = Depends(get_temporal_service)
):
    """Compares topic evolution between two chronological dates or version periods."""
    try:
        return service.compare_temporal_diff(
            topic=req.topic,
            period_from=req.period_from,
            period_to=req.period_to
        )
    except Exception as e:
        logger.error(f"Temporal diff failed: {e}")
        raise HTTPException(status_code=500, detail=f"Temporal diff failed: {str(e)}")


@router.post("/conflict-check", response_model=TemporalConflictResult)
async def check_conflict(
    req: ConflictCheckRequest,
    service: TemporalService = Depends(get_temporal_service)
):
    """Classifies claim divergence into Genuine Contradiction, Version Change, or Temporal Evolution."""
    try:
        return service.check_claim_conflict(
            claim_a=req.claim_a,
            claim_b=req.claim_b,
            timestamp_a=req.timestamp_a,
            timestamp_b=req.timestamp_b,
            doc_a=req.doc_a,
            doc_b=req.doc_b,
            version_a=req.version_a,
            version_b=req.version_b
        )
    except Exception as e:
        logger.error(f"Conflict check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conflict check failed: {str(e)}")
