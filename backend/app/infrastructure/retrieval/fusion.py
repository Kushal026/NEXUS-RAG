"""
Hybrid Fusion Algorithms: Reciprocal Rank Fusion (RRF) and Weighted Score Fusion.
"""
from typing import List, Dict
from app.domain.models import ScoredChunk
from app.core.config import settings
from app.core.logging import logger


class HybridFusion:
    """Combines dense vector and sparse keyword search results."""

    @staticmethod
    def reciprocal_rank_fusion(
        dense_results: List[ScoredChunk],
        sparse_results: List[ScoredChunk],
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        rrf_k: int = settings.RRF_K_CONSTANT,
        top_k: int = 10
    ) -> List[ScoredChunk]:
        """Calculates RRF score across dense and sparse ranking lists."""
        fused_map: Dict[str, ScoredChunk] = {}
        rrf_scores: Dict[str, float] = {}

        # Process Dense results
        for rank, item in enumerate(dense_results, start=1):
            chunk_id = item.chunk.id
            if chunk_id not in fused_map:
                fused_map[chunk_id] = ScoredChunk(
                    chunk=item.chunk,
                    dense_score=item.dense_score,
                    dense_rank=rank
                )
            else:
                fused_map[chunk_id].dense_score = item.dense_score
                fused_map[chunk_id].dense_rank = rank
            
            rrf_contrib = dense_weight * (1.0 / (rrf_k + rank))
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + rrf_contrib

        # Process Sparse results
        for rank, item in enumerate(sparse_results, start=1):
            chunk_id = item.chunk.id
            if chunk_id not in fused_map:
                fused_map[chunk_id] = ScoredChunk(
                    chunk=item.chunk,
                    sparse_score=item.sparse_score,
                    sparse_rank=rank
                )
            else:
                fused_map[chunk_id].sparse_score = item.sparse_score
                fused_map[chunk_id].sparse_rank = rank

            rrf_contrib = sparse_weight * (1.0 / (rrf_k + rank))
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + rrf_contrib

        # Populate rrf_score and final_score
        for chunk_id, scored_chunk in fused_map.items():
            scored_chunk.rrf_score = rrf_scores[chunk_id]
            scored_chunk.final_score = rrf_scores[chunk_id]

        # Sort descending by RRF score
        sorted_results = sorted(fused_map.values(), key=lambda x: x.rrf_score or 0.0, reverse=True)
        return sorted_results[:top_k]

    @staticmethod
    def weighted_score_fusion(
        dense_results: List[ScoredChunk],
        sparse_results: List[ScoredChunk],
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        top_k: int = 10
    ) -> List[ScoredChunk]:
        """Calculates linear weighted combination of normalized scores."""
        fused_map: Dict[str, ScoredChunk] = {}

        for rank, item in enumerate(dense_results, start=1):
            fused_map[item.chunk.id] = ScoredChunk(
                chunk=item.chunk,
                dense_score=item.dense_score,
                dense_rank=rank
            )

        for rank, item in enumerate(sparse_results, start=1):
            c_id = item.chunk.id
            if c_id not in fused_map:
                fused_map[c_id] = ScoredChunk(
                    chunk=item.chunk,
                    sparse_score=item.sparse_score,
                    sparse_rank=rank
                )
            else:
                fused_map[c_id].sparse_score = item.sparse_score
                fused_map[c_id].sparse_rank = rank

        for item in fused_map.values():
            d_s = item.dense_score or 0.0
            s_s = item.sparse_score or 0.0
            item.final_score = (dense_weight * d_s) + (sparse_weight * s_s)

        sorted_results = sorted(fused_map.values(), key=lambda x: x.final_score, reverse=True)
        return sorted_results[:top_k]
