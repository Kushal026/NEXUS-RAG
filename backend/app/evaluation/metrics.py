"""
Information Retrieval Evaluation Metrics: Recall@K, Precision@K, MRR, and NDCG@K.
"""
from typing import List, Dict, Set, Optional
import math
from app.domain.models import EvaluationMetricScores


class RetrievalMetrics:
    """Calculates standard IR metrics for ranked search results against ground truth."""

    @staticmethod
    def recall_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int) -> float:
        if not ground_truth_ids:
            return 0.0
        top_k = retrieved_ids[:k]
        hits = sum(1 for cid in top_k if cid in ground_truth_ids)
        return hits / len(ground_truth_ids)

    @staticmethod
    def precision_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int) -> float:
        if k == 0:
            return 0.0
        top_k = retrieved_ids[:k]
        hits = sum(1 for cid in top_k if cid in ground_truth_ids)
        return hits / k

    @staticmethod
    def mean_reciprocal_rank(retrieved_ids: List[str], ground_truth_ids: Set[str]) -> float:
        for rank, cid in enumerate(retrieved_ids, start=1):
            if cid in ground_truth_ids:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def ndcg_at_k(
        retrieved_ids: List[str],
        ground_truth_relevance: Dict[str, float],
        k: int
    ) -> float:
        """Calculates Normalized Discounted Cumulative Gain (NDCG) at rank K."""
        top_k = retrieved_ids[:k]
        
        # DCG
        dcg = 0.0
        for i, cid in enumerate(top_k):
            rel = ground_truth_relevance.get(cid, 0.0)
            if rel > 0:
                dcg += (2.0 ** rel - 1.0) / math.log2(i + 2)

        # IDCG (Ideal DCG)
        ideal_rels = sorted(ground_truth_relevance.values(), reverse=True)[:k]
        idcg = 0.0
        for i, rel in enumerate(ideal_rels):
            if rel > 0:
                idcg += (2.0 ** rel - 1.0) / math.log2(i + 2)

        return (dcg / idcg) if idcg > 0 else 0.0

    @classmethod
    def compute_all(
        cls,
        retrieved_ids: List[str],
        ground_truth_ids: Set[str],
        ground_truth_relevance: Optional[Dict[str, float]] = None
    ) -> EvaluationMetricScores:
        rel_map = ground_truth_relevance or {cid: 1.0 for cid in ground_truth_ids}
        return EvaluationMetricScores(
            recall_at_1=round(cls.recall_at_k(retrieved_ids, ground_truth_ids, 1), 4),
            recall_at_3=round(cls.recall_at_k(retrieved_ids, ground_truth_ids, 3), 4),
            recall_at_5=round(cls.recall_at_k(retrieved_ids, ground_truth_ids, 5), 4),
            recall_at_10=round(cls.recall_at_k(retrieved_ids, ground_truth_ids, 10), 4),
            precision_at_1=round(cls.precision_at_k(retrieved_ids, ground_truth_ids, 1), 4),
            precision_at_3=round(cls.precision_at_k(retrieved_ids, ground_truth_ids, 3), 4),
            precision_at_5=round(cls.precision_at_k(retrieved_ids, ground_truth_ids, 5), 4),
            precision_at_10=round(cls.precision_at_k(retrieved_ids, ground_truth_ids, 10), 4),
            mrr=round(cls.mean_reciprocal_rank(retrieved_ids, ground_truth_ids), 4),
            ndcg_at_5=round(cls.ndcg_at_k(retrieved_ids, rel_map, 5), 4),
            ndcg_at_10=round(cls.ndcg_at_k(retrieved_ids, rel_map, 10), 4),
        )
