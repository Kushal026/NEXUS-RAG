"""
Cross-Encoder Neural Reranker with heuristic fallback.
"""
from typing import List, Tuple
from app.domain.interfaces import BaseReranker
from app.domain.models import ScoredChunk
from app.core.config import settings
from app.core.logging import logger


class CrossEncoderReranker:
    """Neural cross-encoder reranking using HuggingFace / SentenceTransformers cross-encoder."""

    def __init__(self, model_name: str = settings.RERANKER_MODEL):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            logger.info(f"Loading CrossEncoder model '{self.model_name}'...")
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, scored_chunks: List[ScoredChunk], top_k: int = 10) -> List[ScoredChunk]:
        if not scored_chunks or not query:
            return scored_chunks[:top_k]

        try:
            model = self._get_model()
            # Process up to 50 candidates for neural reranking
            candidates_to_rerank = scored_chunks[:50]
            pairs: List[Tuple[str, str]] = [(query, item.chunk.content) for item in candidates_to_rerank]
            
            # Predict scores in batches
            scores = model.predict(pairs, batch_size=16, show_progress_bar=False)
            
            for idx, item in enumerate(candidates_to_rerank):
                raw_score = float(scores[idx])
                # Sigmoid scaling
                norm_score = 1.0 / (1.0 + 2.71828 ** (-raw_score))
                item.rerank_score = round(norm_score, 4)
                item.final_score = round(norm_score, 4)

            # Sort descending by rerank score
            sorted_chunks = sorted(candidates_to_rerank, key=lambda x: x.rerank_score or 0.0, reverse=True)
            return sorted_chunks[:top_k]

        except Exception as e:
            logger.warning(f"CrossEncoder error: {e}. Falling back to heuristic reranker.")
            fallback = HeuristicReranker()
            return fallback.rerank(query, scored_chunks, top_k=top_k)


class HeuristicReranker:
    """Fast lexical overlap and length-penalty reranker used when neural model is disabled or offline."""

    def rerank(self, query: str, scored_chunks: List[ScoredChunk], top_k: int = 10) -> List[ScoredChunk]:
        q_tokens = set(query.lower().split())
        candidates = scored_chunks[:50]
        for item in candidates:
            c_text = item.chunk.content.lower()
            overlap = sum(1 for t in q_tokens if t in c_text)
            coverage = overlap / max(len(q_tokens), 1)
            # Combine existing final_score with keyword coverage
            item.rerank_score = round(0.4 * item.final_score + 0.6 * coverage, 4)
            item.final_score = item.rerank_score

        sorted_chunks = sorted(candidates, key=lambda x: x.final_score, reverse=True)
        return sorted_chunks[:top_k]


def get_reranker() -> BaseReranker:
    provider = settings.RERANKER_PROVIDER.lower()
    if provider == "none":
        return HeuristicReranker()
    elif provider == "heuristic":
        return HeuristicReranker()
    else:
        return CrossEncoderReranker(model_name=settings.RERANKER_MODEL)
