"""
Retrieval Quality & Evidence Adequacy Evaluator for NEXUS-RAG (Phase 7).
Evaluates relevance, entity coverage, source reliability, redundancy, and contradictions to guide self-correction retries.
"""
from typing import List, Dict, Any, Optional
import re
from app.domain.models import (
    ScoredChunk,
    RetrievalQualityScore,
    SelfCorrectionDecision,
    NLIClassificationType
)
from app.infrastructure.evidence.nli_engine import NLIEngine
from app.infrastructure.evidence.source_reliability_evaluator import SourceReliabilityEvaluator
from app.core.logging import logger


class RetrievalQualityEvaluator:
    """Evaluates multi-dimensional evidence quality and detects missing information gaps."""

    def __init__(
        self,
        nli_engine: Optional[NLIEngine] = None,
        source_evaluator: Optional[SourceReliabilityEvaluator] = None
    ):
        self.nli = nli_engine or NLIEngine()
        self.source_eval = source_evaluator or SourceReliabilityEvaluator()

    def extract_query_key_terms(self, query: str) -> List[str]:
        """Extracts substantive topical nouns, entities, and keywords from the query."""
        stopwords = {
            "what", "is", "the", "and", "how", "does", "explain", "why", "are", "of", "in",
            "for", "with", "to", "a", "an", "on", "can", "between", "difference", "comparison"
        }
        words = re.findall(r"\b[A-Za-z0-9\-_]{3,}\b", query)
        return [w for w in words if w.lower() not in stopwords]

    def evaluate_quality(
        self,
        query: str,
        retrieved_chunks: List[ScoredChunk]
    ) -> RetrievalQualityScore:
        """
        Calculates multi-factor retrieval quality score and determines whether to proceed or retry.
        """
        if not retrieved_chunks:
            return RetrievalQualityScore(
                overall_quality=0.0,
                relevance_score=0.0,
                coverage_score=0.0,
                source_quality_score=0.0,
                redundancy_score=0.0,
                has_contradictions=False,
                missing_gaps=["Entire document context missing"],
                recommended_decision=SelfCorrectionDecision.ABSTAIN,
                evaluation_reason="No relevant chunks retrieved from knowledge vault."
            )

        # 1. Relevance Score (Max & top-3 average)
        max_score = max(sc.final_score for sc in retrieved_chunks)
        top_avg_score = sum(sc.final_score for sc in retrieved_chunks[:3]) / min(3, len(retrieved_chunks))
        relevance_score = min(1.0, (0.5 * max_score) + (0.5 * top_avg_score))

        # 2. Key Terms & Entity Coverage
        key_terms = self.extract_query_key_terms(query)
        combined_text = " ".join([sc.chunk.content for sc in retrieved_chunks]).lower()

        found_terms = [t for t in key_terms if t.lower() in combined_text]
        missing_terms = [t for t in key_terms if t.lower() not in combined_text]

        coverage_score = len(found_terms) / max(1, len(key_terms))

        # 3. Source Quality Score
        source_scores = []
        for sc in retrieved_chunks[:4]:
            fname = sc.chunk.metadata.get("filename", "unknown")
            sq = self.source_eval.evaluate_source(
                document_filename=fname,
                chunk_content=sc.chunk.content,
                document_metadata=sc.chunk.metadata
            )
            source_scores.append(sq.overall_score)
        avg_source_quality = sum(source_scores) / max(1, len(source_scores))

        # 4. Redundancy / Diversity Score (1.0 = highly diverse, 0.0 = completely duplicate)
        unique_docs = len(set(sc.chunk.metadata.get("filename", "") for sc in retrieved_chunks))
        redundancy_score = min(1.0, unique_docs / max(1, min(len(retrieved_chunks), 3)))

        # 5. Contradiction Detection across candidate sentences
        has_contradictions = False
        sample_sentences = []
        for sc in retrieved_chunks[:3]:
            sentences = re.split(r"(?<=[.!?])\s+", sc.chunk.content)
            for s in sentences:
                if len(s.strip()) > 20:
                    sample_sentences.append(s.strip())

        for i in range(min(5, len(sample_sentences))):
            for j in range(i + 1, min(6, len(sample_sentences))):
                nli_res = self.nli.evaluate_pair(sample_sentences[i], sample_sentences[j])
                if nli_res.verdict in (
                    NLIClassificationType.CONTRADICTION,
                    NLIClassificationType.PARTIAL_CONTRADICTION
                ):
                    has_contradictions = True
                    break
            if has_contradictions:
                break

        # Overall Composite Quality Score
        overall = round(
            (0.35 * relevance_score) +
            (0.35 * coverage_score) +
            (0.15 * avg_source_quality) +
            (0.15 * redundancy_score),
            3
        )

        # Decision Logic
        if has_contradictions and overall > 0.40:
            decision = SelfCorrectionDecision.RETRY_RESOLVE_CONTRADICTION
            reason = "Conflicting evidence statements detected across candidate chunks; targeted disambiguation required."
        elif len(missing_terms) > 0 and (overall < 0.65 or coverage_score < 0.70):
            decision = SelfCorrectionDecision.RETRY_MISSING_EVIDENCE
            reason = f"Missing key query entities/terms ({', '.join(missing_terms)}); alternate query expansion required."
        elif overall >= 0.60:
            decision = SelfCorrectionDecision.GENERATE
            reason = f"Evidence meets sufficiency threshold (Quality: {overall:.2f}, Coverage: {coverage_score*100:.0f}%)."
        else:
            decision = SelfCorrectionDecision.RETRY_MISSING_EVIDENCE
            reason = f"Retrieval confidence ({overall:.2f}) is below optimal threshold; query reformulation recommended."

        return RetrievalQualityScore(
            overall_quality=overall,
            relevance_score=round(relevance_score, 3),
            coverage_score=round(coverage_score, 3),
            source_quality_score=round(avg_source_quality, 3),
            redundancy_score=round(redundancy_score, 3),
            has_contradictions=has_contradictions,
            missing_gaps=missing_terms,
            recommended_decision=decision,
            evaluation_reason=reason
        )
