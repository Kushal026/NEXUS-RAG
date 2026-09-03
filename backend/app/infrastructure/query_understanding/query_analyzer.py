"""
Query Analyzer module for NEXUS-RAG.
Extracts intent, keywords, named entities, date constraints, and document filters.
"""
from typing import List, Dict, Any, Tuple
import re
from app.domain.models import QueryAnalysis, ExtractedConstraints
from app.core.logging import logger


class QueryAnalyzer:
    """Analyzes search queries to extract semantic intent, entities, and structured constraints."""

    # Common stopwords for keyword filtering
    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with",
        "about", "against", "between", "into", "through", "during", "before", "after",
        "above", "below", "from", "up", "down", "of", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
        "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "can", "will", "just",
        "should", "now", "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "having", "do", "does", "did", "doing", "tell", "me", "what", "which", "who"
    }

    def analyze(self, raw_query: str) -> QueryAnalysis:
        cleaned_query = raw_query.strip()
        constraints = ExtractedConstraints()

        # 1. Extract explicit inline filter syntax: doc:x.pdf, author:name, after:YYYY, etc.
        # Extract doc:
        doc_matches = re.findall(r"\bdoc:(\S+)", cleaned_query, flags=re.IGNORECASE)
        if doc_matches:
            constraints.target_documents.extend(doc_matches)
            cleaned_query = re.sub(r"\bdoc:\S+", "", cleaned_query, flags=re.IGNORECASE).strip()

        # Extract filetype:
        type_matches = re.findall(r"\b(?:filetype|type):(\S+)", cleaned_query, flags=re.IGNORECASE)
        if type_matches:
            constraints.target_file_types.extend(type_matches)
            cleaned_query = re.sub(r"\b(?:filetype|type):\S+", "", cleaned_query, flags=re.IGNORECASE).strip()

        # Extract author:
        author_matches = re.findall(r"\bauthor:(\S+)", cleaned_query, flags=re.IGNORECASE)
        if author_matches:
            constraints.target_authors.extend(author_matches)
            cleaned_query = re.sub(r"\bauthor:\S+", "", cleaned_query, flags=re.IGNORECASE).strip()

        # Extract tag:
        tag_matches = re.findall(r"\btag:(\S+)", cleaned_query, flags=re.IGNORECASE)
        if tag_matches:
            constraints.tags.extend(tag_matches)
            cleaned_query = re.sub(r"\btag:\S+", "", cleaned_query, flags=re.IGNORECASE).strip()

        # Extract year / date constraints (e.g. after:2023, year:2024, in 2024)
        after_match = re.search(r"\bafter:(\d{4})", cleaned_query, flags=re.IGNORECASE)
        if after_match:
            constraints.date_after = after_match.group(1)
            cleaned_query = re.sub(r"\bafter:\d{4}", "", cleaned_query, flags=re.IGNORECASE).strip()

        before_match = re.search(r"\bbefore:(\d{4})", cleaned_query, flags=re.IGNORECASE)
        if before_match:
            constraints.date_before = before_match.group(1)
            cleaned_query = re.sub(r"\bbefore:\d{4}", "", cleaned_query, flags=re.IGNORECASE).strip()

        year_match = re.search(r"\b(?:in|year:)\s*(\d{4})\b", cleaned_query, flags=re.IGNORECASE)
        if year_match and not constraints.date_after:
            constraints.date_after = year_match.group(1)

        # 2. Extract Entities & Technical Acronyms (e.g., NEXUS-7700, BM25, RRF, RFC-9110, Qubits)
        entity_patterns = [
            r"\b[A-Z]{2,}(?:-[A-Za-z0-9]+)+\b",  # e.g., NEXUS-7700-TX, RFC-9110
            r"\b[A-Z][a-zA-Z0-9]*(?:[A-Z][a-z0-9]+)+\b",  # CamelCase: PostgreSql, PyMuPDF
            r"\b[A-Z]{2,}\b",  # All-caps: RRF, BM25, CPU, NLI, RAG, PDF
        ]
        entities = set()
        for pat in entity_patterns:
            for match in re.findall(pat, cleaned_query):
                if len(match) > 1 and match.lower() not in self.STOPWORDS:
                    entities.add(match)

        # 3. Extract Keywords
        words = re.findall(r"\b[A-Za-z0-9_-]+\b", cleaned_query)
        keywords = [w for w in words if w.lower() not in self.STOPWORDS and len(w) > 1]

        # 4. Classify Intent
        q_lower = cleaned_query.lower()
        if any(w in q_lower for w in ["compare", "versus", "vs", "difference between", "distinction"]):
            intent = "comparative_analysis"
        elif any(w in q_lower for w in ["latest", "recent", "history", "trend", "evolution", "chronology"]) or constraints.date_after:
            intent = "temporal_query"
        elif any(w in q_lower for w in ["overview", "summary", "explain", "how does", "what is"]):
            intent = "conceptual_overview"
        else:
            intent = "factual_lookup"

        # 5. Suggested Retrieval Mode
        # If technical alphanumeric entity is present, hybrid with BM25 boost is critical
        has_strict_entity = any("-" in e or e.isupper() for e in entities)
        suggested_mode = "hybrid_boost_bm25" if has_strict_entity else "hybrid"

        logger.info(f"QueryAnalysis for '{raw_query}': Intent={intent}, Entities={list(entities)}, Keywords={keywords[:5]}")

        return QueryAnalysis(
            original_query=raw_query,
            cleaned_query=cleaned_query,
            intent=intent,
            keywords=keywords,
            entities=list(entities),
            constraints=constraints,
            suggested_retrieval_mode=suggested_mode
        )
