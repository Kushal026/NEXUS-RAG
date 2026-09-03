"""
Targeted Query Rewriter for Self-Correction Recovery in NEXUS-RAG (Phase 7).
Generates precise alternate searches to target missing information gaps and disambiguate conflicting evidence.
"""
from typing import List, Tuple, Optional
import re
from app.domain.models import SelfCorrectionDecision
from app.core.logging import logger


class TargetedQueryRewriter:
    """Generates targeted alternate searches when evidence is incomplete or contradictory."""

    SYNONYM_MAP = {
        "accuracy": ["precision", "performance score", "benchmark results", "evaluation metrics"],
        "architecture": ["structure", "model design", "specifications", "neural components"],
        "retrieval": ["search", "dense indexing", "BM25 keyword matching", "information extraction"],
        "transformer": ["self-attention", "multi-head attention", "encoder decoder network"],
        "quantization": ["FP16", "INT8", "weight compression", "model pruning"],
        "latency": ["inference time", "throughput", "computational delay", "tokens per second"]
    }

    def rewrite_query(
        self,
        original_query: str,
        decision: SelfCorrectionDecision,
        missing_gaps: List[str],
        iteration: int = 2
    ) -> Tuple[str, str]:
        """
        Generates a targeted alternate search query based on the self-correction trigger.
        """
        clean_query = original_query.rstrip("?. ")

        # 1. Contradiction Disambiguation Strategy
        if decision == SelfCorrectionDecision.RETRY_RESOLVE_CONTRADICTION:
            strategy = "contradiction_disambiguation"
            rewritten = f"{clean_query} benchmark evaluation conditions dataset comparison"
            logger.info(f"Iteration {iteration} Contradiction Rewrite: '{rewritten}'")
            return rewritten, strategy

        # 2. Targeted Gap Injection Strategy
        if missing_gaps and len(missing_gaps) > 0:
            strategy = "missing_gap_targeting"
            gap_str = " ".join(missing_gaps[:3])
            rewritten = f"{clean_query} {gap_str} detailed technical explanation"
            logger.info(f"Iteration {iteration} Gap-Targeted Rewrite: '{rewritten}'")
            return rewritten, strategy

        # 3. Domain Synonym & Lexical Expansion Strategy
        words = clean_query.lower().split()
        for term, syns in self.SYNONYM_MAP.items():
            if term in words:
                strategy = "domain_synonym_expansion"
                alt_term = syns[min(iteration - 2, len(syns) - 1)]
                rewritten = f"{clean_query} ({alt_term})"
                logger.info(f"Iteration {iteration} Synonym Rewrite: '{rewritten}'")
                return rewritten, strategy

        # 4. Context Broadening Fallback
        strategy = "context_broadening"
        rewritten = f"{clean_query} overview principles specifications and implementation"
        logger.info(f"Iteration {iteration} Context Broadening Rewrite: '{rewritten}'")
        return rewritten, strategy
