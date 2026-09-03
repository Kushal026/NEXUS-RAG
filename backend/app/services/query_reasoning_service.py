"""
Query Reasoning Service orchestrating multi-hop planning, step-by-step retrieval execution,
intermediate fact extraction, query rewriting, stop conditions, and cross-hop synthesis.
"""
from typing import List, Dict, Optional, Tuple
import time
import re
from app.domain.models import (
    RetrievalPlan,
    PlanStep,
    StepEvidence,
    MultiHopReasoningTrace,
    EvidenceSynthesisResult,
    RetrievalMode,
    ScoredChunk,
    QueryCategory
)
from app.infrastructure.query_reasoning.query_classifier import QueryClassifier
from app.infrastructure.query_reasoning.query_decomposer import QueryDecomposer
from app.infrastructure.query_reasoning.retrieval_planner import RetrievalPlanner
from app.infrastructure.query_reasoning.query_rewriter import QueryRewriter
from app.infrastructure.llm.provider import get_llm_provider
from app.services.retrieval_service import RetrievalService
from app.core.logging import logger


class QueryReasoningService:
    """Executes multi-hop retrieval reasoning with intermediate evidence tracking and safety guardrails."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        planner: Optional[RetrievalPlanner] = None,
        rewriter: Optional[QueryRewriter] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.planner = planner or RetrievalPlanner()
        self.rewriter = rewriter or QueryRewriter()
        self.llm_provider = get_llm_provider()

    def generate_plan(self, query: str) -> RetrievalPlan:
        """Generates and returns structured retrieval plan without executing."""
        return self.planner.create_plan(query)

    def execute_reasoning_pipeline(
        self,
        query: str,
        max_hops: int = 4,
        confidence_threshold: float = 0.85
    ) -> EvidenceSynthesisResult:
        """Executes full multi-hop retrieval reasoning with intermediate evidence tracking."""
        start_time = time.time()
        plan = self.planner.create_plan(query)

        # Fast path for simple/single-hop queries
        if not plan.is_multihop:
            logger.info(f"Executing fast single-hop retrieval for '{query}'")
            scored_chunks, r_trace = self.retrieval_service.retrieve_with_trace(query=query)
            
            synthesis = self.llm_provider.generate_synthesis(query=query, evidence_chunks=scored_chunks)
            synthesis.retrieval_trace = r_trace
            
            # Form single-hop reasoning trace
            step_ev = StepEvidence(
                step_number=1,
                sub_query=query,
                retrieved_chunks=scored_chunks,
                extracted_facts=[c.chunk.content[:100] for c in scored_chunks[:3]],
                discovered_entities=r_trace.query_analysis.entities if r_trace.query_analysis else [],
                confidence_score=scored_chunks[0].final_score if scored_chunks else 0.0,
                execution_time_ms=r_trace.total_pipeline_time_ms
            )
            synthesis.multihop_trace = MultiHopReasoningTrace(
                plan=plan,
                step_evidences=[step_ev],
                total_hops_executed=1,
                stop_reason="single_hop_direct",
                all_accumulated_chunks=scored_chunks,
                total_reasoning_time_ms=round((time.time() - start_time) * 1000, 2)
            )
            return synthesis

        # Multi-Hop Iterative Execution
        logger.info(f"Starting Multi-Hop Reasoning Execution for '{query}' ({len(plan.steps)} planned steps)")
        step_evidences: List[StepEvidence] = []
        all_chunks: List[ScoredChunk] = []
        seen_chunk_ids = set()
        accumulated_facts: List[str] = []
        accumulated_entities: List[str] = []

        stop_reason = "plan_completed"

        for step in plan.steps:
            if len(step_evidences) >= max_hops:
                stop_reason = "max_hops_reached"
                break

            step_t0 = time.time()
            step.status = "in_progress"

            # 1. Context injection from previous hops
            exec_query = step.sub_query
            if step.depends_on_step and accumulated_entities:
                exec_query = self.rewriter.inject_intermediate_context(
                    sub_query=step.sub_query,
                    prior_facts=accumulated_facts,
                    prior_entities=accumulated_entities
                )

            # 2. Configure retrieval mode
            mode = RetrievalMode(top_k=20, rerank_top_k=5)
            if step.retrieval_strategy == "sparse_bm25":
                mode.use_dense = False
                mode.use_sparse = True
            elif step.retrieval_strategy == "dense":
                mode.use_dense = True
                mode.use_sparse = False
            elif step.retrieval_strategy == "hybrid_boost_bm25":
                mode.sparse_weight = 0.7
                mode.dense_weight = 0.3

            # 3. Retrieve chunks for step
            step_chunks, step_trace = self.retrieval_service.retrieve_with_trace(query=exec_query, mode=mode)
            top_score = step_chunks[0].final_score if step_chunks else 0.0

            # 4. Check for low confidence rewrite
            was_rewritten = False
            orig_q = None
            if top_score < 0.40:
                was_rewritten = True
                orig_q = exec_query
                rewritten_q, _ = self.rewriter.rewrite_for_low_confidence(exec_query, top_score)
                exec_query = rewritten_q
                retry_chunks, _ = self.retrieval_service.retrieve_with_trace(query=exec_query, mode=mode)
                if retry_chunks and (not step_chunks or retry_chunks[0].final_score > top_score):
                    step_chunks = retry_chunks
                    top_score = retry_chunks[0].final_score

            step.status = "completed"
            step_time = round((time.time() - step_t0) * 1000, 2)

            # 5. Extract facts & entities
            step_entities = step_trace.query_analysis.entities if step_trace.query_analysis else []
            step_facts = [c.chunk.content.split("\n")[0] for c in step_chunks[:2] if c.chunk.content]

            accumulated_entities.extend(step_entities)
            accumulated_facts.extend(step_facts)

            # Dedup and accumulate chunks
            for sc in step_chunks:
                if sc.chunk.id not in seen_chunk_ids:
                    seen_chunk_ids.add(sc.chunk.id)
                    all_chunks.append(sc)

            evidence_item = StepEvidence(
                step_number=step.step_number,
                sub_query=exec_query,
                retrieved_chunks=step_chunks,
                extracted_facts=step_facts,
                discovered_entities=step_entities,
                confidence_score=round(top_score, 4),
                was_rewritten=was_rewritten,
                original_sub_query=orig_q,
                execution_time_ms=step_time
            )
            step_evidences.append(evidence_item)

        # Final Multi-Hop Synthesis across all accumulated evidence chunks
        total_time_ms = round((time.time() - start_time) * 1000, 2)
        synthesis = self.llm_provider.generate_synthesis(query=query, evidence_chunks=all_chunks[:10])

        synthesis.multihop_trace = MultiHopReasoningTrace(
            plan=plan,
            step_evidences=step_evidences,
            total_hops_executed=len(step_evidences),
            stop_reason=stop_reason,
            all_accumulated_chunks=all_chunks,
            total_reasoning_time_ms=total_time_ms
        )

        logger.info(f"Multi-Hop reasoning finished in {total_time_ms}ms ({len(step_evidences)} hops, {len(all_chunks)} chunks)")
        return synthesis
