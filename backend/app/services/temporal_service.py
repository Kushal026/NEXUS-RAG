"""
Temporal Service orchestrating time-travel queries, temporal diffing across epochs,
document versioning, lineage tracking, and conflict resolution.
"""
from typing import List, Dict, Any, Optional
import time
import re
from datetime import datetime
from app.domain.models import (
    Document,
    DocumentChunk,
    DocumentMetadata,
    DocumentVersionInfo,
    TemporalFilter,
    TemporalDiffResult,
    TemporalClaimDiff,
    TemporalConflictResult,
    TemporalConflictType,
    EvidenceSynthesisResult,
    RetrievalMode
)
from app.infrastructure.temporal.temporal_extractor import TemporalExtractor
from app.infrastructure.temporal.temporal_filter import TemporalFilterEngine
from app.infrastructure.temporal.temporal_conflict_resolver import TemporalConflictResolver
from app.services.retrieval_service import RetrievalService
from app.infrastructure.llm.provider import get_llm_provider
from app.core.logging import logger


class TemporalService:
    """Provides bi-temporal intelligence, version lineage, and chronological diff comparison."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        conflict_resolver: Optional[TemporalConflictResolver] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.conflict_resolver = conflict_resolver or TemporalConflictResolver()
        self.extractor = TemporalExtractor()
        self.llm_provider = get_llm_provider()

    def query_as_of(
        self,
        query: str,
        as_of_date: str,
        top_k: int = 5
    ) -> EvidenceSynthesisResult:
        """Retrieves and synthesizes state strictly valid as of a historical date/year."""
        t_filter = TemporalFilter(as_of_date=as_of_date, latest_only=False)
        mode = RetrievalMode(temporal_filter=t_filter, top_k=top_k * 2, rerank_top_k=top_k)

        chunks, trace = self.retrieval_service.retrieve_with_trace(query=query, mode=mode)
        synthesis = self.llm_provider.generate_synthesis(query=f"[As of {as_of_date}] {query}", evidence_chunks=chunks)
        synthesis.retrieval_trace = trace
        return synthesis

    def compare_temporal_diff(
        self,
        topic: str,
        period_from: str,
        period_to: str
    ) -> TemporalDiffResult:
        """Computes delta/evolution between two points in time or versions."""
        logger.info(f"Computing temporal diff for topic '{topic}' between {period_from} and {period_to}")
        
        # 1. Retrieve chunks valid in earlier epoch
        filter_from = TemporalFilter(as_of_date=period_from, latest_only=False)
        chunks_from, _ = self.retrieval_service.retrieve_with_trace(
            query=topic,
            mode=RetrievalMode(temporal_filter=filter_from, top_k=10, rerank_top_k=4)
        )

        # 2. Retrieve chunks valid in later epoch
        filter_to = TemporalFilter(as_of_date=period_to, latest_only=False)
        chunks_to, _ = self.retrieval_service.retrieve_with_trace(
            query=topic,
            mode=RetrievalMode(temporal_filter=filter_to, top_k=10, rerank_top_k=4)
        )

        text_from = " ".join([c.chunk.content for c in chunks_from]) if chunks_from else f"State in {period_from}"
        text_to = " ".join([c.chunk.content for c in chunks_to]) if chunks_to else f"State in {period_to}"

        # Detect specific attributes changed (e.g. temperature, architecture, protocol)
        detected_changes: List[TemporalClaimDiff] = []

        # Check numeric and technical differences
        num_from = re.findall(r"\b\d+(?:\.\d+)?\s*(?:millikelvin|mK|qubits|GHz|ms|tokens)?\b", text_from, flags=re.IGNORECASE)
        num_to = re.findall(r"\b\d+(?:\.\d+)?\s*(?:millikelvin|mK|qubits|GHz|ms|tokens)?\b", text_to, flags=re.IGNORECASE)

        if num_from and num_to and num_from[0] != num_to[0]:
            detected_changes.append(
                TemporalClaimDiff(
                    attribute="Metric Specification",
                    prior_state=num_from[0],
                    prior_date=period_from,
                    current_state=num_to[0],
                    current_date=period_to,
                    change_type="updated",
                    explanation=f"Specification value evolved from {num_from[0]} in {period_from} to {num_to[0]} in {period_to}."
                )
            )

        diff_summary = (
            f"Temporal comparison for '{topic}' from {period_from} to {period_to}: "
            f"Identified {len(detected_changes)} specification evolution(s) across historical versions."
        )

        return TemporalDiffResult(
            topic=topic,
            period_from=period_from,
            period_to=period_to,
            diff_summary=diff_summary,
            detected_changes=detected_changes,
            confidence=0.92
        )

    def check_claim_conflict(
        self,
        claim_a: str,
        claim_b: str,
        timestamp_a: Optional[str] = None,
        timestamp_b: Optional[str] = None,
        doc_a: Optional[str] = None,
        doc_b: Optional[str] = None,
        version_a: Optional[str] = None,
        version_b: Optional[str] = None
    ) -> TemporalConflictResult:
        """Determines if divergence is genuine contradiction, version supersession, or temporal evolution."""
        return self.conflict_resolver.resolve_conflict(
            claim_a=claim_a,
            claim_b=claim_b,
            timestamp_a=timestamp_a,
            timestamp_b=timestamp_b,
            doc_a=doc_a,
            doc_b=doc_b,
            version_a=version_a,
            version_b=version_b
        )
