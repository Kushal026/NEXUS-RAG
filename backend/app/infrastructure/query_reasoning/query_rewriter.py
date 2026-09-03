"""
Query Rewriter for reformulating low-confidence sub-queries and injecting intermediate hop facts.
"""
from typing import List, Tuple, Optional
import re
from app.core.logging import logger


class QueryRewriter:
    """Reformulates sub-queries when retrieval confidence is low or when intermediate facts are discovered."""

    SYNONYMS = {
        "techniques": ["methods", "algorithms", "approaches", "mechanisms"],
        "evaluate": ["benchmark", "assess", "performance results", "experimental comparison"],
        "proposed": ["introduced", "authored", "developed", "created"],
        "architecture": ["structure", "hardware design", "specifications", "system model"],
        "temperature": ["operating conditions", "cryogenic threshold", "thermal limits"]
    }

    def rewrite_for_low_confidence(self, sub_query: str, low_score: float) -> Tuple[str, str]:
        """Rewrites a query to broaden lexical coverage when initial confidence is $< 0.4$."""
        words = sub_query.lower().split()
        rewritten = sub_query
        strategy = "synonym_expansion"

        for word, syn_list in self.SYNONYMS.items():
            if word in words:
                # Add primary synonym
                syn = syn_list[0]
                rewritten = re.sub(rf"\b{word}\b", f"({word} OR {syn})", rewritten, flags=re.IGNORECASE)
                break

        if rewritten == sub_query:
            # Fallback: append general conceptual term
            rewritten = f"{sub_query.rstrip('?')} technical specifications and overview?"
            strategy = "context_broadening"

        logger.info(f"Rewrote low-confidence query ({low_score:.2f}) -> '{rewritten}' [{strategy}]")
        return rewritten, strategy

    def inject_intermediate_context(
        self,
        sub_query: str,
        prior_facts: List[str],
        prior_entities: List[str]
    ) -> str:
        """Injects concrete entities or facts discovered from prior hops into dependent sub-queries."""
        if not prior_entities and not prior_facts:
            return sub_query

        # If sub_query contains generic placeholders like 'the techniques', 'those methods', replace with entity
        enhanced_query = sub_query
        if prior_entities:
            top_entity = prior_entities[0]
            if not re.search(rf"\b{re.escape(top_entity)}\b", enhanced_query, flags=re.IGNORECASE):
                # Contextualize with discovered entity
                enhanced_query = f"{top_entity} {sub_query}"

        logger.info(f"Injected intermediate hop context into sub-query: '{enhanced_query}'")
        return enhanced_query
