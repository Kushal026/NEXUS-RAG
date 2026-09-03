"""
Query Decomposer breaking complex multi-faceted inquiries into atomic sub-questions with dependency graphs.
"""
import re
from typing import List, Tuple
from app.domain.models import PlanStep
from app.core.logging import logger


class QueryDecomposer:
    """Decomposes compound or multi-hop inquiries into sequential atomic sub-questions."""

    def decompose(self, query: str) -> List[PlanStep]:
        q_cleaned = query.strip().rstrip("?")
        q_lower = q_cleaned.lower()

        steps: List[PlanStep] = []

        # Check for standard multi-hop research pattern (e.g. "What techniques in X, who proposed them, and how evaluated?")
        # 1. Look for explicit comma/conjunction splits
        parts = re.split(r",\s*and\s+(?:also\s+)?|,\s*(?:who|what|how|where|when)\s+|\s+and\s+(?:how|who|what|why)\s+", q_cleaned, flags=re.IGNORECASE)
        
        # Clean parts
        raw_clauses = [p.strip() for p in parts if len(p.strip().split()) >= 2]

        if len(raw_clauses) >= 2:
            # Multi-part question
            # Extract subject / primary entity from first clause if possible (e.g. "paper X", "NEXUS-7700-TX")
            entity_match = re.search(r"\b(in|of|for|about)\s+([A-Za-z0-9\-_]+(?:\s+[A-Za-z0-9\-_]+){0,2})", raw_clauses[0], flags=re.IGNORECASE)
            subject = entity_match.group(2) if entity_match else ""

            for idx, clause in enumerate(raw_clauses, start=1):
                sub_q = clause.strip()
                if not sub_q.endswith("?"):
                    sub_q += "?"
                
                # If subsequent clause has relative pronouns ("them", "it", "those"), contextualize with subject
                if idx > 1 and subject:
                    sub_q = re.sub(r"\bthem\b", f"the techniques in {subject}", sub_q, flags=re.IGNORECASE)
                    sub_q = re.sub(r"\bit\b", subject, sub_q, flags=re.IGNORECASE)

                # Ensure question starts properly
                if not re.match(r"^(what|who|how|where|when|why|identify|find|compare|explain)\b", sub_q, flags=re.IGNORECASE):
                    sub_q = f"What is {sub_q}"

                strategy = self._assign_strategy(sub_q)
                dep = idx - 1 if idx > 1 else None

                step = PlanStep(
                    step_number=idx,
                    sub_query=sub_q,
                    retrieval_strategy=strategy,
                    depends_on_step=dep,
                    description=f"Step {idx}: Atomic retrieval for '{clause}'",
                    status="pending"
                )
                steps.append(step)
        else:
            # Single clause question
            strategy = self._assign_strategy(query)
            steps.append(
                PlanStep(
                    step_number=1,
                    sub_query=query if query.endswith("?") else f"{query}?",
                    retrieval_strategy=strategy,
                    depends_on_step=None,
                    description="Direct atomic retrieval",
                    status="pending"
                )
            )

        logger.info(f"Decomposed '{query}' into {len(steps)} plan steps")
        return steps

    def _assign_strategy(self, sub_query: str) -> str:
        q_l = sub_query.lower()
        # If technical part numbers or exact codes exist, boost BM25
        if re.search(r"\b[A-Z0-9]+-[A-Z0-9]+|\brfc-\d+|\bv\d+\.\d+\b", sub_query):
            return "hybrid_boost_bm25"
        elif re.search(r"\b(author|who|creator|inventor|proposed by|published by)\b", q_l):
            return "hybrid_boost_bm25"
        elif re.search(r"\b(concept|overview|meaning|theory|principle)\b", q_l):
            return "dense"
        return "hybrid"
