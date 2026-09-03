"""
Query API endpoints: Hybrid search retrieval and full evidence synthesis with citations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.services.retrieval_service import RetrievalService
from app.services.evidence_service import EvidenceService
from app.schemas.requests import QueryRequest
from app.domain.models import ScoredChunk, EvidenceSynthesisResult, RetrievalMode, QueryAnalysis

router = APIRouter(prefix="/query", tags=["Query & Evidence Search"])

_retrieval_service: Optional[RetrievalService] = None
_evidence_service: Optional[EvidenceService] = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service


def get_evidence_service(
    retrieval_svc: RetrievalService = Depends(get_retrieval_service)
) -> EvidenceService:
    global _evidence_service
    if _evidence_service is None:
        _evidence_service = EvidenceService(retrieval_service=retrieval_svc)
    return _evidence_service


@router.post("/analyze", response_model=QueryAnalysis)
async def analyze_query(
    req: QueryRequest,
    service: RetrievalService = Depends(get_retrieval_service)
):
    """Analyze query intent, extract named entities, keywords, and explicit constraints."""
    return service.query_analyzer.analyze(req.query)


@router.post("/search")
async def search_retrieval(
    req: QueryRequest,
    service: RetrievalService = Depends(get_retrieval_service)
):
    """Execute multi-stage hybrid retrieval (Dense + BM25 + RRF + Cross-Encoder) with full trace."""
    try:
        mode = RetrievalMode(
            use_dense=req.use_dense,
            use_sparse=req.use_sparse,
            use_reranker=req.use_reranker,
            dense_weight=req.dense_weight,
            sparse_weight=req.sparse_weight,
            top_k=req.top_k,
            rerank_top_k=req.rerank_top_k,
            metadata_filter=req.metadata_filter
        )
        results, trace = service.retrieve_with_trace(query=req.query, mode=mode)
        return {
            "results": results,
            "trace": trace
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/synthesize", response_model=EvidenceSynthesisResult)
async def synthesize_evidence(
    req: QueryRequest,
    service: EvidenceService = Depends(get_evidence_service)
):
    """Perform hybrid retrieval and synthesize structured evidence with claim-level citations."""
    try:
        mode = RetrievalMode(
            use_dense=req.use_dense,
            use_sparse=req.use_sparse,
            use_reranker=req.use_reranker,
            dense_weight=req.dense_weight,
            sparse_weight=req.sparse_weight,
            top_k=req.top_k,
            rerank_top_k=req.rerank_top_k,
            metadata_filter=req.metadata_filter
        )
        synthesis = service.synthesize_evidence(query=req.query, mode=mode)
        return synthesis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence synthesis failed: {str(e)}")


@router.post("/stream")
async def stream_evidence_synthesis(
    req: QueryRequest,
    service: EvidenceService = Depends(get_evidence_service)
):
    """Streams token-by-token evidence synthesis via Server-Sent Events (SSE)."""
    from fastapi.responses import StreamingResponse

    mode = RetrievalMode(
        use_dense=req.use_dense,
        use_sparse=req.use_sparse,
        use_reranker=req.use_reranker,
        dense_weight=req.dense_weight,
        sparse_weight=req.sparse_weight,
        top_k=req.top_k,
        rerank_top_k=req.rerank_top_k,
        metadata_filter=req.metadata_filter
    )
    generator = service.synthesize_evidence_stream(query=req.query, mode=mode)
    return StreamingResponse(generator, media_type="text/event-stream")
