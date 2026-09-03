"""
API Endpoints for Phase 6 — Evidence Intelligence Engine.
Provides deep evidence analysis, contradiction detection, source reliability, and coverage validation.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from app.domain.models import (
    EvidenceIntelligenceReport,
    NLIResult,
    SourceReliabilityScore,
    GroupedClaimEvidence,
    RetrievalMode
)
from app.services.evidence_intelligence_service import EvidenceIntelligenceService
from app.core.logging import logger

router = APIRouter(prefix="/evidence", tags=["Evidence Intelligence Engine"])

evidence_intel_service = EvidenceIntelligenceService()


class EvidenceAnalysisRequest(BaseModel):
    query: str
    top_k: int = 10
    use_dense: bool = True
    use_sparse: bool = True
    use_reranker: bool = True


class NLIRequest(BaseModel):
    premise: str
    hypothesis: str


class SourceQualityRequest(BaseModel):
    filename: str
    content: Optional[str] = ""


class GroupClaimsRequest(BaseModel):
    claims: List[str]


@router.post("/analyze", response_model=EvidenceIntelligenceReport)
def analyze_query_evidence(request: EvidenceAnalysisRequest):
    """
    Executes full Evidence Intelligence pipeline:
    NLI Contradiction Detection -> Source Quality Scoring -> Claim Grouping -> Coverage & Unknown Evaluation.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    mode = RetrievalMode(
        use_dense=request.use_dense,
        use_sparse=request.use_sparse,
        use_reranker=request.use_reranker,
        top_k=request.top_k,
        rerank_top_k=min(5, request.top_k)
    )

    return evidence_intel_service.analyze_evidence(query=request.query, mode=mode)


@router.post("/nli", response_model=NLIResult)
def evaluate_pairwise_nli(request: NLIRequest):
    """
    Evaluates agreement, direct contradiction, partial contradiction, differing conditions, or temporal drift.
    """
    if not request.premise.strip() or not request.hypothesis.strip():
        raise HTTPException(status_code=400, detail="Both premise and hypothesis are required.")

    return evidence_intel_service.evaluate_pairwise_nli(
        premise=request.premise,
        hypothesis=request.hypothesis
    )


@router.post("/source-quality", response_model=SourceReliabilityScore)
def evaluate_source_quality(request: SourceQualityRequest):
    """
    Computes transparent multi-factor reliability score for an evidence document.
    """
    return evidence_intel_service.evaluate_source_quality(
        filename=request.filename,
        content=request.content or ""
    )
