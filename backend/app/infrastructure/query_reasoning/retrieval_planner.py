"""
Retrieval Planner formulating structured execution plans and dependency chains.
"""
from typing import Optional
import uuid
from app.domain.models import RetrievalPlan, QueryCategory, PlanStep
from app.infrastructure.query_reasoning.query_classifier import QueryClassifier
from app.infrastructure.query_reasoning.query_decomposer import QueryDecomposer
from app.core.logging import logger


class RetrievalPlanner:
    """Constructs multi-hop or single-hop execution plans."""

    def __init__(
        self,
        classifier: Optional[QueryClassifier] = None,
        decomposer: Optional[QueryDecomposer] = None
    ):
        self.classifier = classifier or QueryClassifier()
        self.decomposer = decomposer or QueryDecomposer()

    def create_plan(self, query: str) -> RetrievalPlan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        category = self.classifier.classify(query)

        is_multihop = category in (QueryCategory.MULTI_HOP, QueryCategory.COMPARATIVE, QueryCategory.RESEARCH)

        if is_multihop:
            steps = self.decomposer.decompose(query)
            # Guarantee at least 2 steps for multi-hop
            if len(steps) == 1 and category == QueryCategory.MULTI_HOP:
                # Add context expansion step
                steps.append(
                    PlanStep(
                        step_number=2,
                        sub_query=f"Retrieve evaluation and impact details for {query}?",
                        retrieval_strategy="hybrid",
                        depends_on_step=1,
                        description="Step 2: Subsequent evaluation retrieval",
                        status="pending"
                    )
                )
            reasoning_summary = f"Multi-hop research plan: Decomposed inquiry into {len(steps)} sequential retrieval steps with context passing."
        else:
            steps = [
                PlanStep(
                    step_number=1,
                    sub_query=query,
                    retrieval_strategy="hybrid",
                    depends_on_step=None,
                    description="Single-hop direct retrieval",
                    status="pending"
                )
            ]
            reasoning_summary = f"Direct execution plan: Single-step {category.value} retrieval."

        plan = RetrievalPlan(
            plan_id=plan_id,
            original_query=query,
            query_category=category,
            reasoning_summary=reasoning_summary,
            steps=steps,
            estimated_hops=len(steps),
            is_multihop=len(steps) > 1
        )

        logger.info(f"Generated RetrievalPlan '{plan_id}' ({category.value}, {len(steps)} steps)")
        return plan
