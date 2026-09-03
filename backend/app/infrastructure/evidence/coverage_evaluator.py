"""
Evidence Coverage & Insufficient Evidence Evaluator for NEXUS-RAG (Phase 6).
Computes coverage percentages, composite evidence scoring breakdowns, and safe unknown-handling triggers.
"""
from typing import List, Dict, Any, Tuple, Optional
from app.domain.models import (
    GroupedClaimEvidence,
    ScoredChunk,
    CompositeScoreBreakdown,
    SourceReliabilityScore
)
from app.core.logging import logger


class EvidenceCoverageEvaluator:
    """Evaluates answer claim coverage and computes transparent composite evidence metrics."""

    COVERAGE_THRESHOLD = 40.0       # Minimum percentage of claims that must be supported
    RELEVANCE_THRESHOLD = 0.30      # Minimum chunk score to consider evidence present

    def evaluate_coverage(
        self,
        grouped_claims: List[GroupedClaimEvidence],
        retrieved_chunks: List[ScoredChunk],
        source_qualities: Dict[str, SourceReliabilityScore]
    ) -> Tuple[float, int, int, int, bool, Optional[str], CompositeScoreBreakdown]:
        """
        Computes coverage metrics, unknown detection, and composite evidence score breakdown.
        """
        total_claims = len(grouped_claims)
        if total_claims == 0 or not retrieved_chunks:
            breakdown = CompositeScoreBreakdown(
                relevance_component=0.0,
                source_reliability_component=0.0,
                temporal_relevance_component=0.0,
                agreement_component=0.0,
                coverage_component=0.0,
                formula_weights={"relevance": 0.25, "source_reliability": 0.25, "temporal": 0.15, "agreement": 0.15, "coverage": 0.20},
                final_composite_score=0.0
            )
            return 0.0, 0, 0, 0, True, "No relevant documents or claims found in the knowledge vault.", breakdown

        supported_count = sum(1 for c in grouped_claims if c.verification_status in ("supported", "partially_supported"))
        contradicted_count = sum(1 for c in grouped_claims if c.verification_status == "contradicted")
        unsupported_count = sum(1 for c in grouped_claims if c.verification_status == "insufficient_evidence")

        coverage_pct = round((supported_count / total_claims) * 100.0, 1)

        # Check for Insufficient Evidence Condition
        max_chunk_score = max((sc.final_score for sc in retrieved_chunks), default=0.0)
        is_insufficient = False
        insufficient_reason = None

        if max_chunk_score < self.RELEVANCE_THRESHOLD:
            is_insufficient = True
            insufficient_reason = f"Maximum retrieved evidence relevance ({max_chunk_score:.2f}) is below confidence threshold ({self.RELEVANCE_THRESHOLD:.2f})."
        elif coverage_pct < self.COVERAGE_THRESHOLD and total_claims > 1:
            is_insufficient = True
            insufficient_reason = f"Evidence coverage ({coverage_pct:.1f}%) is below minimum threshold ({self.COVERAGE_THRESHOLD:.1f}%)."

        # Compute Composite Evidence Score Breakdown
        avg_relevance = min(1.0, sum(sc.final_score for sc in retrieved_chunks[:5]) / min(5, len(retrieved_chunks)))
        
        # Source reliability
        if source_qualities:
            avg_source_rel = sum(sq.overall_score for sq in source_qualities.values()) / len(source_qualities)
        else:
            avg_source_rel = 0.60

        # Temporal relevance
        temporal_rel = 0.85

        # Agreement factor (penalize if contradictions exist)
        if contradicted_count > 0:
            agreement_factor = max(0.20, 1.0 - (contradicted_count * 0.35))
        else:
            agreement_factor = 0.95

        coverage_factor = coverage_pct / 100.0

        weights = {
            "relevance": 0.25,
            "source_reliability": 0.25,
            "temporal": 0.15,
            "agreement": 0.15,
            "coverage": 0.20
        }

        final_composite = round(
            (weights["relevance"] * avg_relevance) +
            (weights["source_reliability"] * avg_source_rel) +
            (weights["temporal"] * temporal_rel) +
            (weights["agreement"] * agreement_factor) +
            (weights["coverage"] * coverage_factor),
            3
        )

        breakdown = CompositeScoreBreakdown(
            relevance_component=round(avg_relevance, 3),
            source_reliability_component=round(avg_source_rel, 3),
            temporal_relevance_component=round(temporal_rel, 3),
            agreement_component=round(agreement_factor, 3),
            coverage_component=round(coverage_factor, 3),
            formula_weights=weights,
            final_composite_score=final_composite
        )

        return (
            coverage_pct,
            supported_count,
            contradicted_count,
            unsupported_count,
            is_insufficient,
            insufficient_reason,
            breakdown
        )
