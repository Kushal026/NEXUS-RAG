"""
Evidence Intelligence Service for NEXUS-RAG (Phase 6).
Orchestrates claim-level evidence grouping, contradiction detection, source quality evaluation, and coverage calculation.
"""
from typing import List, Dict, Any, Optional
import time
from app.domain.models import (
    RetrievalMode,
    EvidenceIntelligenceReport,
    GroupedClaimEvidence,
    SourceReliabilityScore,
    NLIResult,
    ScoredChunk
)
from app.services.retrieval_service import RetrievalService
from app.infrastructure.evidence.nli_engine import NLIEngine
from app.infrastructure.evidence.source_reliability_evaluator import SourceReliabilityEvaluator
from app.infrastructure.evidence.claim_grouper import ClaimEvidenceGrouper
from app.infrastructure.evidence.coverage_evaluator import EvidenceCoverageEvaluator
from app.infrastructure.llm.provider import get_llm_provider
from app.core.logging import logger


class EvidenceIntelligenceService:
    """Coordinates deep evidence analysis, contradiction detection, source reliability, and coverage validation."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.nli_engine = NLIEngine()
        self.source_evaluator = SourceReliabilityEvaluator()
        self.claim_grouper = ClaimEvidenceGrouper(
            nli_engine=self.nli_engine,
            reliability_evaluator=self.source_evaluator
        )
        self.coverage_evaluator = EvidenceCoverageEvaluator()
        self.llm_provider = get_llm_provider()

    def analyze_evidence(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None
    ) -> EvidenceIntelligenceReport:
        """
        Executes complete Phase 6 Evidence Intelligence pipeline.
        """
        start_time = time.time()
        logger.info(f"Running Evidence Intelligence Analysis for query: '{query}'")

        # 1. Retrieve ranked candidates
        evidence_chunks, trace = self.retrieval_service.retrieve_with_trace(query=query, mode=mode)

        # 2. Extract key claims from preliminary synthesis or top retrieved chunks
        if not evidence_chunks:
            # Safe Unknown Rejection
            return self._build_insufficient_evidence_report(
                query=query,
                reason="No candidate documents or passages found in knowledge vault.",
                start_time=start_time
            )

        # Extract claims from top context passages
        combined_text = "\n".join([c.chunk.content for c in evidence_chunks[:4]])
        claims = self.claim_grouper.extract_atomic_claims(combined_text)

        if not claims:
            claims = [f"Direct context retrieved for: {query}"]

        # 3. Group evidence around claims (Supporting vs Contradicting)
        grouped_claims = self.claim_grouper.group_evidence_for_claims(
            claims=claims,
            evidence_chunks=evidence_chunks
        )

        # 4. Extract all unique source reliability scores
        source_matrix: Dict[str, SourceReliabilityScore] = {}
        for gc in grouped_claims:
            for fname, score in gc.source_qualities.items():
                if fname not in source_matrix:
                    source_matrix[fname] = score

        # 5. Evaluate Evidence Coverage & Unknown condition
        (
            coverage_pct,
            supported_count,
            contradicted_count,
            unsupported_count,
            is_insufficient,
            insufficient_reason,
            score_breakdown
        ) = self.coverage_evaluator.evaluate_coverage(
            grouped_claims=grouped_claims,
            retrieved_chunks=evidence_chunks,
            source_qualities=source_matrix
        )

        # 6. Build synthesis text based on evidence findings
        if is_insufficient:
            synthesis_md = (
                f"### ⚠ Insufficient Evidence in Knowledge Vault\n\n"
                f"**Query**: *\"{query}\"*\n\n"
                f"> **System Notice**: NEXUS-RAG evidence intelligence rejected synthesis to prevent hallucination.\n"
                f"> **Reason**: {insufficient_reason}\n\n"
                f"#### Evidence Assessment\n"
                f"- **Evaluated Claims**: {len(grouped_claims)}\n"
                f"- **Verified Coverage**: `{coverage_pct}%`\n"
                f"- **Missing Context**: Specific factual assertions for this query lack authoritative document citations."
            )
        else:
            # Build rich grounded synthesis with claim status and conflict warnings
            claim_summaries = []
            for gc in grouped_claims:
                status_icon = "✅" if gc.verification_status == "supported" else ("⚠" if gc.has_conflict else "❓")
                conflict_note = f"\n  > ⚠ **Conflicting Evidence**: {gc.conflict_explanation}" if gc.has_conflict else ""
                sources_str = ", ".join([f"`{c.document_filename}` (P.{c.page_number or '1'})" for c in gc.supporting_citations[:2]]) or "Context body"
                claim_summaries.append(
                    f"- {status_icon} **{gc.statement}**\n  *Evidence: {sources_str}* (Confidence: {int(gc.confidence_score*100)}%){conflict_note}"
                )

            synthesis_md = (
                f"### Evidence-Grounded Intelligence Report\n\n"
                f"**Evidence Coverage**: `{coverage_pct}%` • **Composite Score**: `{score_breakdown.final_composite_score:.3f}` • **Analyzed Sources**: `{len(source_matrix)}`\n\n"
                f"#### Verified Claim Findings\n"
                + "\n\n".join(claim_summaries)
            )

        exec_ms = round((time.time() - start_time) * 1000, 2)

        return EvidenceIntelligenceReport(
            query=query,
            synthesis_markdown=synthesis_md,
            grouped_claims=grouped_claims,
            evidence_coverage_percentage=coverage_pct,
            supported_claims_count=supported_count,
            contradicted_claims_count=contradicted_count,
            unsupported_claims_count=unsupported_count,
            is_insufficient_evidence=is_insufficient,
            insufficient_evidence_reason=insufficient_reason,
            composite_evidence_score=score_breakdown.final_composite_score,
            score_breakdown=score_breakdown,
            source_reliability_matrix=source_matrix,
            retrieved_chunks=evidence_chunks,
            execution_time_ms=exec_ms,
            model_used="evidence_intelligence_v1"
        )

    def evaluate_pairwise_nli(self, premise: str, hypothesis: str) -> NLIResult:
        """Evaluates pairwise statement NLI contradiction and entailment."""
        return self.nli_engine.evaluate_pair(premise, hypothesis)

    def evaluate_source_quality(self, filename: str, content: str = "") -> SourceReliabilityScore:
        """Evaluates source reliability factors for a given document."""
        return self.source_evaluator.evaluate_source(filename, content)

    def _build_insufficient_evidence_report(
        self,
        query: str,
        reason: str,
        start_time: float
    ) -> EvidenceIntelligenceReport:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return EvidenceIntelligenceReport(
            query=query,
            synthesis_markdown=(
                f"### ⚠ Insufficient Evidence in Knowledge Vault\n\n"
                f"The system searched the document repository but found **insufficient evidence** to answer: *\"{query}\"*.\n\n"
                f"- **Reason**: {reason}\n"
                f"- **Zero-Hallucination Policy**: NEXUS-RAG strictly rejects ungrounded queries."
            ),
            grouped_claims=[],
            evidence_coverage_percentage=0.0,
            supported_claims_count=0,
            contradicted_claims_count=0,
            unsupported_claims_count=0,
            is_insufficient_evidence=True,
            insufficient_evidence_reason=reason,
            composite_evidence_score=0.0,
            execution_time_ms=exec_ms
        )
