"""
Self-Correcting Retrieval Engine Service for NEXUS-RAG (Phase 7).
Coordinates iterative retrieval, quality evaluation, targeted query rewriting, cross-iteration evidence accumulation,
post-generation claim verification, and safe abstention.
"""
from typing import List, Dict, Any, Optional
import time
from app.domain.models import (
    RetrievalMode,
    SelfCorrectingRAGResult,
    SelfCorrectionIteration,
    SelfCorrectionDecision,
    RetrievalQualityScore,
    AnswerVerificationResult,
    ScoredChunk
)
from app.services.retrieval_service import RetrievalService
from app.infrastructure.self_correction.retrieval_quality_evaluator import RetrievalQualityEvaluator
from app.infrastructure.self_correction.targeted_query_rewriter import TargetedQueryRewriter
from app.infrastructure.self_correction.evidence_accumulator import EvidenceAccumulator
from app.infrastructure.self_correction.answer_verifier import AnswerVerifier
from app.infrastructure.llm.provider import get_llm_provider
from app.core.logging import logger


class SelfCorrectingService:
    """Coordinates the iterative self-correcting RAG pipeline with bounded retries."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        max_iterations: int = 3
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.quality_evaluator = RetrievalQualityEvaluator()
        self.query_rewriter = TargetedQueryRewriter()
        self.accumulator = EvidenceAccumulator()
        self.verifier = AnswerVerifier()
        self.llm_provider = get_llm_provider()
        self.max_iterations = max_iterations

    def execute_self_correcting_rag(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None,
        max_iterations: Optional[int] = None
    ) -> SelfCorrectingRAGResult:
        """
        Executes the iterative retrieval loop with quality evaluation, targeted rewriting, and verification.
        """
        start_time = time.time()
        max_iters = max_iterations or self.max_iterations
        logger.info(f"Starting Self-Correcting RAG for query: '{query}' (Max Iterations: {max_iters})")

        accumulated_chunks: List[ScoredChunk] = []
        iterations_trace: List[SelfCorrectionIteration] = []
        current_query = query
        current_strategy = None
        last_quality = None

        for iter_num in range(1, max_iters + 1):
            iter_start = time.time()
            logger.info(f"--- Iteration {iter_num}/{max_iters}: Query='{current_query}' ---")

            # 1. Retrieve candidates
            new_chunks, _ = self.retrieval_service.retrieve_with_trace(
                query=current_query,
                mode=mode
            )

            # 2. Accumulate without discarding prior useful knowledge
            accumulated_chunks = self.accumulator.accumulate(
                existing_chunks=accumulated_chunks,
                new_chunks=new_chunks
            )

            # 3. Evaluate combined evidence quality
            quality = self.quality_evaluator.evaluate_quality(
                query=query,
                retrieved_chunks=accumulated_chunks
            )
            last_quality = quality

            # 4. Record iteration trace
            iter_trace = SelfCorrectionIteration(
                iteration_number=iter_num,
                search_query=current_query,
                rewrite_strategy=current_strategy,
                retrieved_chunks_count=len(new_chunks),
                accumulated_chunks_count=len(accumulated_chunks),
                quality_evaluation=quality,
                decision_taken=quality.recommended_decision.value,
                notes=quality.evaluation_reason
            )
            iterations_trace.append(iter_trace)

            # 5. Check Termination Conditions
            if quality.recommended_decision == SelfCorrectionDecision.GENERATE:
                logger.info(f"Iteration {iter_num}: Evidence sufficient (Quality: {quality.overall_quality:.2f}). Proceeding to generation.")
                break

            if iter_num < max_iters:
                # 6. Generate targeted rewritten query for next iteration
                next_query, strategy = self.query_rewriter.rewrite_query(
                    original_query=query,
                    decision=quality.recommended_decision,
                    missing_gaps=quality.missing_gaps,
                    iteration=iter_num + 1
                )
                current_query = next_query
                current_strategy = strategy
            else:
                logger.warning(f"Max iterations ({max_iters}) reached without achieving optimal quality.")

        total_iters = len(iterations_trace)

        # 7. Check for Abstention
        if not accumulated_chunks or (last_quality and last_quality.overall_quality < 0.35 and last_quality.coverage_score < 0.40):
            exec_ms = round((time.time() - start_time) * 1000, 2)
            abstention_reason = (
                f"Retrieved evidence quality ({last_quality.overall_quality if last_quality else 0.0:.2f}) "
                f"and coverage ({last_quality.coverage_score*100 if last_quality else 0.0:.0f}%) remained below "
                f"acceptable thresholds after {total_iters} retrieval recovery attempts."
            )
            return SelfCorrectingRAGResult(
                query=query,
                final_answer_markdown=(
                    f"### ⚠ Insufficient Evidence (Self-Correction Abstained)\n\n"
                    f"**Query**: *\"{query}\"*\n\n"
                    f"> **System Notice**: NEXUS-RAG attempted {total_iters} retrieval iterations with targeted query reformulations, but could not obtain sufficient authoritative evidence.\n"
                    f"> **Abstention Reason**: {abstention_reason}\n\n"
                    f"#### Attempted Search Iterations:\n"
                    + "\n".join([f"- **Attempt {it.iteration_number}** (`{it.rewrite_strategy or 'original'}`): *\"{it.search_query}\"* → {it.retrieved_chunks_count} chunks (Quality: {it.quality_evaluation.overall_quality if it.quality_evaluation else 0:.2f})" for it in iterations_trace])
                ),
                status="abstained",
                total_iterations=total_iters,
                max_iterations_allowed=max_iters,
                iterations_trace=iterations_trace,
                accumulated_chunks=accumulated_chunks,
                verification=None,
                final_evidence_coverage=0.0,
                is_abstained=True,
                abstention_reason=abstention_reason,
                execution_time_ms=exec_ms,
                metrics={
                    "retrieval_iterations": total_iters,
                    "recovered": False,
                    "abstained": True,
                    "unsupported_claim_rate": 0.0,
                    "accumulated_chunks": len(accumulated_chunks)
                }
            )

        # 8. Generate Draft Synthesis
        raw_synthesis = self.llm_provider.generate_synthesis(
            query=query,
            evidence_chunks=accumulated_chunks
        )

        # 9. Run Post-Generation Answer Verifier
        verification = self.verifier.verify_answer(
            raw_answer=raw_synthesis.synthesis_markdown,
            accumulated_chunks=accumulated_chunks
        )

        status = "recovered" if total_iters > 1 else "first_pass_success"
        coverage_pct = round(
            (verification.supported_claims_count / max(1, len(verification.extracted_claims))) * 100,
            1
        ) if verification.extracted_claims else 100.0

        exec_ms = round((time.time() - start_time) * 1000, 2)

        return SelfCorrectingRAGResult(
            query=query,
            final_answer_markdown=verification.final_answer,
            status=status,
            total_iterations=total_iters,
            max_iterations_allowed=max_iters,
            iterations_trace=iterations_trace,
            accumulated_chunks=accumulated_chunks,
            verification=verification,
            final_evidence_coverage=coverage_pct,
            is_abstained=False,
            abstention_reason=None,
            execution_time_ms=exec_ms,
            metrics={
                "retrieval_iterations": total_iters,
                "recovered": (total_iters > 1),
                "abstained": False,
                "unsupported_claim_rate": verification.unsupported_claim_rate,
                "final_evidence_coverage": coverage_pct,
                "accumulated_chunks": len(accumulated_chunks)
            },
            model_used="self_correcting_rag_v1"
        )
