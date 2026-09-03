"""
Gap Detector for NEXUS Research Agent (Phase 9).
Evaluates accumulated evidence against research sub-questions, detects missing topical areas,
and generates targeted follow-up queries.
"""
from typing import List, Dict, Tuple, Optional
import re
from app.domain.models import ResearchPlan, ResearchSubQuestion, ScoredChunk
from app.core.logging import logger


class GapDetector:
    """Evaluates sub-question evidence coverage and formulates targeted recovery queries."""

    def evaluate_plan_gaps(
        self,
        plan: ResearchPlan,
        accumulated_chunks: List[ScoredChunk]
    ) -> Tuple[List[str], List[ResearchSubQuestion]]:
        """
        Evaluates which sub-questions have sufficient evidence and produces follow-up queries for gaps.
        Returns: (follow_up_queries, updated_sub_questions)
        """
        combined_text = " ".join([sc.chunk.content.lower() for sc in accumulated_chunks])
        updated_sub_questions: List[ResearchSubQuestion] = []
        follow_up_queries: List[str] = []

        for sq in plan.sub_questions:
            sq_copy = sq.model_copy()
            # Extract key substantive terms from question

            words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", sq.question) if w.lower() not in (
                "what", "where", "when", "which", "how", "underlying", "applied", "currently", "specific", "known"
            )]

            matched_terms = [w for w in words if w in combined_text]
            coverage = len(matched_terms) / max(1, len(words))

            # Associate matched evidence chunks
            matched_evidence_ids = []
            for sc in accumulated_chunks:
                c_text = sc.chunk.content.lower()
                if any(w in c_text for w in words[:3]):
                    matched_evidence_ids.append(sc.chunk.id)

            sq_copy.retrieved_evidence_ids = list(set(matched_evidence_ids))

            if coverage >= 0.50 and len(matched_evidence_ids) >= 1:
                sq_copy.status = "answered"
                sq_copy.key_findings_summary = f"Corroborated by {len(sq_copy.retrieved_evidence_ids)} retrieved evidence passage(s)."
            else:
                sq_copy.status = "partial_gap"
                missing_terms = [w for w in words if w not in combined_text]
                gap_query = f"{sq.question} {' '.join(missing_terms[:3])}".strip()
                follow_up_queries.append(gap_query)
                sq_copy.key_findings_summary = f"Information gap detected: Missing empirical data for {', '.join(missing_terms[:3]) or 'key parameters'}."

            updated_sub_questions.append(sq_copy)

        logger.info(f"Gap Detection: {len(follow_up_queries)} follow-up queries generated across {len(plan.sub_questions)} sub-questions.")
        return follow_up_queries, updated_sub_questions
