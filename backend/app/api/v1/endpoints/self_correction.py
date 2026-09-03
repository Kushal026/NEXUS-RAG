"""
API Endpoints for Phase 7 — Self-Correcting Retrieval Engine.
Provides iterative retrieval execution, quality evaluation, and post-generation answer verification.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from app.domain.models import (
    SelfCorrectingRAGResult,
    RetrievalQualityScore,
    AnswerVerificationResult,
    RetrievalMode,
    DocumentChunk,
    ScoredChunk
)
from app.services.self_correcting_service import SelfCorrectingService
from app.core.logging import logger

router = APIRouter(prefix="/self-correction", tags=["Self-Correcting Retrieval Engine"])

self_correcting_service = SelfCorrectingService()


class SelfCorrectingQueryRequest(BaseModel):
    query: str
    max_iterations: int = 3
    top_k: int = 8
    use_dense: bool = True
    use_sparse: bool = True
    use_reranker: bool = True


class QualityEvaluationRequest(BaseModel):
    query: str
    chunk_texts: List[str]


class VerifyAnswerRequest(BaseModel):
    raw_answer: str
    evidence_texts: List[str]


@router.post("/query", response_model=SelfCorrectingRAGResult)
def execute_self_correcting_query(request: SelfCorrectingQueryRequest):
    """
    Executes the full Self-Correcting RAG loop:
    Retrieve -> Evaluate Evidence -> Rewrite if needed -> Accumulate -> Generate -> Verify Claims -> Return.
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

    return self_correcting_service.execute_self_correcting_rag(
        query=request.query,
        mode=mode,
        max_iterations=request.max_iterations
    )


@router.post("/evaluate-quality", response_model=RetrievalQualityScore)
def evaluate_evidence_quality(request: QualityEvaluationRequest):
    """
    Evaluates retrieval quality and produces gap analysis on arbitrary candidate texts.
    """
    scored_chunks = []
    for i, txt in enumerate(request.chunk_texts):
        c = DocumentChunk(
            id=f"c-{i}",
            document_id=f"doc-{i}",
            chunk_index=i,
            content=txt,
            span={"start_char": 0, "end_char": len(txt), "page_number": 1},
            metadata={"filename": f"sample_doc_{i+1}.pdf"}
        )
        scored_chunks.append(ScoredChunk(chunk=c, final_score=0.85))

    return self_correcting_service.quality_evaluator.evaluate_quality(
        query=request.query,
        retrieved_chunks=scored_chunks
    )


@router.post("/verify-answer", response_model=AnswerVerificationResult)
def verify_answer_claims(request: VerifyAnswerRequest):
    """
    Extracts atomic claims from a draft answer and verifies each against evidence texts using NLI.
    """
    scored_chunks = []
    for i, txt in enumerate(request.evidence_texts):
        c = DocumentChunk(
            id=f"c-{i}",
            document_id=f"doc-{i}",
            chunk_index=i,
            content=txt,
            span={"start_char": 0, "end_char": len(txt), "page_number": 1},
            metadata={"filename": f"evidence_doc_{i+1}.pdf"}
        )
        scored_chunks.append(ScoredChunk(chunk=c, final_score=0.90))

    return self_correcting_service.verifier.verify_answer(
        raw_answer=request.raw_answer,
        accumulated_chunks=scored_chunks
    )
