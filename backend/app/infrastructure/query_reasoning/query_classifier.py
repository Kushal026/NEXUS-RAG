"""
Query Classifier categorizing incoming queries into structural complexity types.
"""
import re
from app.domain.models import QueryCategory
from app.core.logging import logger


class QueryClassifier:
    """Classifies user queries to determine whether multi-hop planning or direct retrieval is optimal."""

    COMPARATIVE_PATTERNS = [
        r"\bcompare\b", r"\bversus\b", r"\bvs\.?\b", r"\bdifference between\b",
        r"\bwhich is better\b", r"\bpros and cons\b", r"\bsimilarities\b"
    ]

    TEMPORAL_PATTERNS = [
        r"\btimeline\b", r"\bhistory of\b", r"\bevolution of\b", r"\bafter\b",
        r"\bbefore\b", r"\bsince \d{4}\b", r"\bin \d{4}\b", r"\bfirst introduced\b",
        r"\blater papers\b", r"\bsubsequent\b", r"\boriginally\b"
    ]

    ANALYTICAL_PATTERNS = [
        r"\bwhy\b", r"\bhow does\b", r"\bexplain the mechanism\b", r"\broot cause\b",
        r"\btrade-?offs?\b", r"\barchitectural impact\b", r"\bimplications\b"
    ]

    MULTI_HOP_PATTERNS = [
        r"\band then\b", r"\band how\b", r"\band who\b", r"\band what\b",
        r"\bwho (introduced|proposed|authored|developed|created)\b.*\bhow\b",
        r"\bwhat (techniques|methods|algorithms)\b.*\bwho\b.*\bhow\b",
        r"\bintroduced in .*, who .*, and\b",
        r"\bfirst .*, second .*\b"
    ]

    RESEARCH_PATTERNS = [
        r"\bsurvey\b", r"\bcomprehensive analysis\b", r"\bliterature review\b",
        r"\bstate of the art\b", r"\bsota\b", r"\bevaluate all\b"
    ]

    def classify(self, query: str) -> QueryCategory:
        q_lower = query.strip().lower()

        # 1. Multi-hop check: questions asking for multiple chained steps
        clause_count = len(re.split(r",\s*and\s+|\s+and\s+how\s+|\s+and\s+who\s+|\s+and\s+what\s+|\?|\band then\b", q_lower))
        has_multihop_phrases = any(re.search(p, q_lower) for p in self.MULTI_HOP_PATTERNS)

        if has_multihop_phrases or (clause_count >= 3 and ("who" in q_lower or "what" in q_lower or "how" in q_lower)):
            logger.info(f"Classified query '{query}' as MULTI_HOP (clauses={clause_count})")
            return QueryCategory.MULTI_HOP

        # 2. Comparative
        if any(re.search(p, q_lower) for p in self.COMPARATIVE_PATTERNS):
            return QueryCategory.COMPARATIVE

        # 3. Temporal
        if any(re.search(p, q_lower) for p in self.TEMPORAL_PATTERNS):
            return QueryCategory.TEMPORAL

        # 4. Research / Survey
        if any(re.search(p, q_lower) for p in self.RESEARCH_PATTERNS):
            return QueryCategory.RESEARCH

        # 5. Analytical
        if any(re.search(p, q_lower) for p in self.ANALYTICAL_PATTERNS):
            return QueryCategory.ANALYTICAL

        # 6. Simple Factual vs Semantic Overview
        words = q_lower.split()
        if len(words) <= 7 or re.search(r"\b(what is|where is|when was|who is|define|specs|rfc|version)\b", q_lower):
            return QueryCategory.SIMPLE_FACTUAL

        return QueryCategory.SEMANTIC
