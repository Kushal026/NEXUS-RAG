"""
Source Reliability Scoring Engine for NEXUS-RAG (Phase 6).
Evaluates document and passage authority, recency, source type, corroboration, and metadata quality transparently.
"""
from typing import Dict, List, Optional, Any
import re
from datetime import datetime
from app.domain.models import SourceReliabilityScore, DocumentChunk
from app.core.logging import logger


class SourceReliabilityEvaluator:
    """Computes transparent, multi-factor reliability and quality scores for evidence sources."""

    AUTHORITY_PATTERNS = [
        r"\b(?:OpenAI|DeepMind|Google(?:\s+Research)?|Stanford|MIT|Harvard|Meta(?:\s+AI)?|Anthropic|Microsoft|UC\s+Berkeley|CMU)\b",
        r"\b(?:Vaswani|Hinton|LeCun|Bengio|Altman|Hassabis|Karpathy|Sutskever)\b"
    ]

    def evaluate_source(
        self,
        document_filename: str,
        chunk_content: str = "",
        document_metadata: Optional[Dict[str, Any]] = None,
        corroboration_count: int = 1
    ) -> SourceReliabilityScore:
        """
        Calculates a transparent multi-factor reliability score for a document source.
        """
        meta = document_metadata or {}
        fname_lower = document_filename.lower()

        # 1. Source Type Score
        if fname_lower.endswith(".pdf") or "paper" in fname_lower or "arxiv" in fname_lower or "ieee" in fname_lower:
            doc_type = "academic_paper"
            type_score = 0.95
        elif fname_lower.endswith(".docx") or "spec" in fname_lower or "rfc" in fname_lower or "whitepaper" in fname_lower:
            doc_type = "technical_specification"
            type_score = 0.90
        elif "benchmark" in fname_lower or "eval" in fname_lower or fname_lower.endswith(".csv"):
            doc_type = "benchmark_dataset_report"
            type_score = 0.85
        elif fname_lower.endswith(".md") or fname_lower.endswith(".txt"):
            doc_type = "structured_notes_or_documentation"
            type_score = 0.75
        else:
            doc_type = "unstructured_document"
            type_score = 0.55

        # 2. Authority Score
        has_author = bool(meta.get("author"))
        full_text = f"{document_filename} {chunk_content} {str(meta)}"
        has_top_org = any(re.search(pat, full_text, re.IGNORECASE) for pat in self.AUTHORITY_PATTERNS)

        if has_top_org and has_author:
            auth_score = 0.98
        elif has_top_org:
            auth_score = 0.92
        elif has_author:
            auth_score = 0.80
        else:
            auth_score = 0.60

        # 3. Recency Score
        pub_year = None
        for m in re.finditer(r"\b(20[12]\d)\b", full_text):
            try:
                pub_year = int(m.group(1))
            except ValueError:
                pass

        curr_year = 2026
        if pub_year:
            age = max(0, curr_year - pub_year)
            recency_score = max(0.50, round(1.0 - (age * 0.05), 2))
        else:
            recency_score = 0.75

        # 4. Corroboration Score
        if corroboration_count >= 3:
            corrob_score = 0.95
        elif corroboration_count == 2:
            corrob_score = 0.85
        else:
            corrob_score = 0.65

        # 5. Citation / Metadata Quality Score
        has_page = "page" in full_text.lower() or meta.get("page_count") is not None
        has_section = bool(meta.get("section_title") or "#" in chunk_content)

        if has_page and has_section:
            cit_qual_score = 0.95
        elif has_page or has_section:
            cit_qual_score = 0.85
        else:
            cit_qual_score = 0.70

        # Formulaic weighted composite calculation
        overall = round(
            (0.30 * type_score) +
            (0.25 * auth_score) +
            (0.15 * recency_score) +
            (0.20 * corrob_score) +
            (0.10 * cit_qual_score),
            3
        )

        expl = (
            f"Calculated via Type ({type_score:.2f} × 30%) + Authority ({auth_score:.2f} × 25%) + "
            f"Recency ({recency_score:.2f} × 15%) + Corroboration ({corrob_score:.2f} × 20%) + "
            f"Citation Metadata ({cit_qual_score:.2f} × 10%)."
        )

        return SourceReliabilityScore(
            document_filename=document_filename,
            overall_score=overall,
            source_type_score=type_score,
            authority_score=auth_score,
            recency_score=recency_score,
            corroboration_score=corrob_score,
            citation_quality_score=cit_qual_score,
            document_type=doc_type,
            explanation=expl
        )
