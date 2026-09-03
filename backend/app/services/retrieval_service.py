"""
Advanced Retrieval Service orchestrating Query Understanding, Dense & BM25 Multi-Channel Search,
Reciprocal Rank Fusion, Top-50 -> Top-10 Cross-Encoder Reranking, and Observability Tracing.
"""
from typing import List, Optional, Dict, Any, Tuple
import time
from app.domain.models import (
    ScoredChunk,
    RetrievalMode,
    RetrievalTrace,
    StageCandidate,
    QueryAnalysis
)
from app.infrastructure.query_understanding.query_analyzer import QueryAnalyzer
from app.infrastructure.embeddings.embedder import get_embedder
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.infrastructure.retrieval.fusion import HybridFusion
from app.infrastructure.retrieval.reranker import get_reranker
from app.core.config import settings
from app.core.logging import logger


class RetrievalService:
    """Coordinates hybrid multi-stage retrieval pipeline with observability tracing."""

    def __init__(
        self,
        vector_store: Optional[DenseVectorStore] = None,
        keyword_store: Optional[BM25KeywordStore] = None
    ):
        self.vector_store = vector_store or DenseVectorStore()
        self.keyword_store = keyword_store or BM25KeywordStore()
        self.query_analyzer = QueryAnalyzer()
        self.embedder = get_embedder()
        self.reranker = get_reranker()

    def _to_stage_candidate(self, sc: ScoredChunk, rank: int, score: float) -> StageCandidate:
        chunk = sc.chunk
        fname = chunk.metadata.get("filename", "Unknown")
        return StageCandidate(
            chunk_id=chunk.id,
            document_filename=fname,
            page_number=chunk.span.page_number,
            score=round(score, 4),
            rank=rank,
            content_snippet=chunk.content[:140] + ("..." if len(chunk.content) > 140 else "")
        )

    def retrieve_with_trace(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None
    ) -> Tuple[List[ScoredChunk], RetrievalTrace]:
        cfg = mode or RetrievalMode()
        total_start = time.time()
        stage_latencies: Dict[str, float] = {}

        # 1. Query Understanding, Constraint & Temporal Extraction
        t0 = time.time()
        analysis = self.query_analyzer.analyze(query)
        
        from app.infrastructure.temporal.temporal_extractor import TemporalExtractor
        t_extractor = TemporalExtractor()
        auto_t_filter, cleaned_q = t_extractor.extract_temporal_filter(query)
        active_t_filter = cfg.temporal_filter or auto_t_filter

        stage_latencies["query_understanding_ms"] = round((time.time() - t0) * 1000, 2)

        # Merge extracted constraints with mode filters
        active_filters = dict(cfg.metadata_filter or {})
        if analysis.constraints.target_documents:
            active_filters["target_documents"] = analysis.constraints.target_documents
        if analysis.constraints.target_file_types:
            active_filters["target_file_types"] = analysis.constraints.target_file_types
        if analysis.constraints.target_authors:
            active_filters["target_authors"] = analysis.constraints.target_authors

        dense_results: List[ScoredChunk] = []
        sparse_results: List[ScoredChunk] = []

        # 2. Dense Vector Search (Top-50)
        if cfg.use_dense:
            t_vec = time.time()
            q_vector = self.embedder.embed_query(analysis.cleaned_query)
            dense_results = self.vector_store.search(
                query_vector=q_vector,
                top_k=cfg.vector_top_k,
                filter_metadata=active_filters if active_filters else None,
                temporal_filter=active_t_filter
            )
            stage_latencies["vector_search_ms"] = round((time.time() - t_vec) * 1000, 2)

        # 3. Sparse BM25 Keyword Search (Top-50)
        if cfg.use_sparse:
            t_bm25 = time.time()
            bm25_query = " ".join(analysis.keywords) if analysis.keywords else analysis.cleaned_query
            sparse_results = self.keyword_store.search(
                query=bm25_query,
                top_k=cfg.bm25_top_k,
                filter_metadata=active_filters if active_filters else None,
                temporal_filter=active_t_filter
            )
            stage_latencies["bm25_search_ms"] = round((time.time() - t_bm25) * 1000, 2)

        # 4. Hybrid Reciprocal Rank Fusion (Top-50)
        t_fuse = time.time()
        if cfg.use_dense and cfg.use_sparse:
            # Adjust weights if query analyzer detected strict alphanumeric entity
            dense_w = cfg.dense_weight
            sparse_w = cfg.sparse_weight
            if analysis.suggested_retrieval_mode == "hybrid_boost_bm25":
                sparse_w = max(sparse_w, 0.6)
                dense_w = min(dense_w, 0.4)

            fused_candidates = HybridFusion.reciprocal_rank_fusion(
                dense_results=dense_results,
                sparse_results=sparse_results,
                dense_weight=dense_w,
                sparse_weight=sparse_w,
                top_k=cfg.top_k
            )
        elif cfg.use_dense:
            fused_candidates = dense_results[:cfg.top_k]
        elif cfg.use_sparse:
            fused_candidates = sparse_results[:cfg.top_k]
        else:
            fused_candidates = []
        stage_latencies["fusion_ms"] = round((time.time() - t_fuse) * 1000, 2)

        # 5. Cross-Encoder Neural Reranking (Top-50 -> Top-10)
        t_rerank = time.time()
        if cfg.use_reranker and fused_candidates:
            final_results = self.reranker.rerank(
                query=query,
                scored_chunks=fused_candidates,
                top_k=cfg.rerank_top_k
            )
        else:
            final_results = fused_candidates[:cfg.rerank_top_k]
        stage_latencies["reranking_ms"] = round((time.time() - t_rerank) * 1000, 2)

        total_time_ms = round((time.time() - total_start) * 1000, 2)

        # Build Stage Trace Candidates for UI waterfall
        trace = RetrievalTrace(
            query=query,
            query_analysis=analysis,
            vector_candidates_count=len(dense_results),
            bm25_candidates_count=len(sparse_results),
            fused_candidates_count=len(fused_candidates),
            reranked_candidates_count=len(final_results),
            stage_latencies_ms=stage_latencies,
            vector_top_candidates=[self._to_stage_candidate(sc, r, sc.dense_score or 0.0) for r, sc in enumerate(dense_results[:6], 1)],
            bm25_top_candidates=[self._to_stage_candidate(sc, r, sc.sparse_score or 0.0) for r, sc in enumerate(sparse_results[:6], 1)],
            fused_top_candidates=[self._to_stage_candidate(sc, r, sc.rrf_score or sc.final_score) for r, sc in enumerate(fused_candidates[:6], 1)],
            final_ranked_candidates=[self._to_stage_candidate(sc, r, sc.final_score) for r, sc in enumerate(final_results, 1)],
            total_pipeline_time_ms=total_time_ms
        )

        logger.info(f"Hybrid retrieval finished in {total_time_ms}ms: {len(dense_results)} vec, {len(sparse_results)} bm25 -> {len(final_results)} final")
        return final_results, trace

    def retrieve(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None
    ) -> List[ScoredChunk]:
        """Convenience method returning scored chunks directly."""
        results, _ = self.retrieve_with_trace(query=query, mode=mode)
        return results
