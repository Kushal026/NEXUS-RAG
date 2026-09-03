"""
Research Planner for NEXUS Research Agent (Phase 9).
Decomposes complex research goals into prioritized analytical sub-questions, identifies key entities, and structures retrieval tactics.
"""
from typing import List, Dict, Any, Optional
import re
import uuid
from app.domain.models import ResearchPlan, ResearchSubQuestion
from app.infrastructure.graph.entity_extractor import EntityExtractor
from app.core.logging import logger


class ResearchPlanner:
    """Generates structured research plans from high-level user research goals."""

    def __init__(self, entity_extractor: Optional[EntityExtractor] = None):
        self.entity_extractor = entity_extractor or EntityExtractor()

    def generate_plan(self, goal: str) -> ResearchPlan:
        """
        Decomposes a goal into analytical sub-questions, entities, and hypotheses.
        """
        logger.info(f"Generating research plan for goal: '{goal}'")
        clean_goal = goal.strip()

        # 1. Extract Entities from Goal
        doc_entities = self.entity_extractor.extract_from_text(clean_goal)
        entity_names = list(set(e[0] for e in doc_entities))


        # 2. Decompose Goal into Analytical Sub-Questions
        sub_questions: List[ResearchSubQuestion] = []

        # Tactic 1: Foundational / Overview Subquestion
        sub_questions.append(ResearchSubQuestion(
            id=f"sq-overview-{uuid.uuid4().hex[:4]}",
            question=f"What are the foundational concepts, definitions, and core architectures underlying {clean_goal}?",
            priority=1,
            status="pending"
        ))

        # Tactic 2: Current Approaches / Methods Subquestion
        sub_questions.append(ResearchSubQuestion(
            id=f"sq-methods-{uuid.uuid4().hex[:4]}",
            question=f"What specific models, algorithms, and state-of-the-art methodologies are currently applied in {clean_goal}?",
            priority=1,
            status="pending"
        ))

        # Tactic 3: Empirical Performance & Comparative Benchmarks
        sub_questions.append(ResearchSubQuestion(
            id=f"sq-eval-{uuid.uuid4().hex[:4]}",
            question=f"What are the quantitative performance benchmarks, accuracy metrics, efficiency trade-offs, and empirical results for {clean_goal}?",
            priority=2,
            status="pending"
        ))

        # Tactic 4: Limitations, Gaps, and Failure Modes
        sub_questions.append(ResearchSubQuestion(
            id=f"sq-limits-{uuid.uuid4().hex[:4]}",
            question=f"What are the known limitations, edge cases, vulnerabilities, or contradictory findings in {clean_goal}?",
            priority=3,
            status="pending"
        ))

        # 3. Generate Key Hypotheses
        hypotheses = [
            f"State-of-the-art techniques for '{clean_goal}' show distinct accuracy-latency trade-offs across different benchmark datasets.",
            f"Recent empirical studies exhibit context-dependent variations in methodology and reported metric thresholds."
        ]

        strategy_overview = (
            f"Multi-hop iterative investigation executing hybrid dense-BM25 retrieval, "
            f"knowledge graph neighborhood traversal for identified entities ({', '.join(entity_names) if entity_names else 'domain terms'}), "
            f"NLI contradiction detection, and post-synthesis factual verification."
        )

        return ResearchPlan(
            plan_id=f"plan-{uuid.uuid4().hex[:6]}",
            goal=clean_goal,
            sub_questions=sub_questions,
            identified_entities=entity_names,
            key_hypotheses=hypotheses,
            strategy_overview=strategy_overview
        )
