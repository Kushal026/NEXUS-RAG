"""
Claim-Centric Evidence Grouper for NEXUS-RAG (Phase 6).
Groups supporting and conflicting evidence citations around atomic claims with contradiction explanations.
"""
from typing import List, Dict, Any, Optional
import re
import uuid
from app.domain.models import (
    GroupedClaimEvidence,
    EvidenceCitation,
    ScoredChunk,
    NLIClassificationType,
    SourceReliabilityScore
)
from app.infrastructure.evidence.nli_engine import NLIEngine
from app.infrastructure.evidence.source_reliability_evaluator import SourceReliabilityEvaluator
from app.core.logging import logger


class ClaimEvidenceGrouper:
    """Extracts atomic claims and groups multi-source supporting and conflicting evidence."""

    def __init__(
        self,
        nli_engine: Optional[NLIEngine] = None,
        reliability_evaluator: Optional[SourceReliabilityEvaluator] = None
    ):
        self.nli = nli_engine or NLIEngine()
        self.reliability_eval = reliability_evaluator or SourceReliabilityEvaluator()

    def extract_atomic_claims(self, text: str) -> List[str]:
        """Extracts individual factual sentences/assertions from text."""
        # Clean markdown headers and bullet markers
        lines = text.split("\n")
        sentences: List[str] = []
        for line in lines:
            cleaned_line = re.sub(r"^[#\-\*\d\.\s]+", "", line).strip()
            if len(cleaned_line) < 15:
                continue
            # Split into sentence clauses
            for s in re.split(r"(?<=[.!?])\s+", cleaned_line):
                s_clean = s.strip(" \"'“”")
                if len(s_clean) > 20 and not s_clean.startswith("---") and not s_clean.startswith("####"):
                    sentences.append(s_clean)
        return sentences[:10]  # Focus on top 10 key claims

    def group_evidence_for_claims(
        self,
        claims: List[str],
        evidence_chunks: List[ScoredChunk]
    ) -> List[GroupedClaimEvidence]:
        """
        Evaluates each atomic claim against all retrieved chunks, separating supporting from conflicting evidence.
        """
        grouped_results: List[GroupedClaimEvidence] = []
        doc_counts: Dict[str, int] = {}
        for sc in evidence_chunks:
            fname = sc.chunk.metadata.get("filename", "Unknown")
            doc_counts[fname] = doc_counts.get(fname, 0) + 1

        for claim_text in claims:
            supporting: List[EvidenceCitation] = []
            contradicting: List[EvidenceCitation] = []
            conflict_reasons: List[str] = []
            source_scores: Dict[str, SourceReliabilityScore] = {}

            for sc in evidence_chunks:
                chunk = sc.chunk
                fname = chunk.metadata.get("filename", "Doc")
                page = chunk.span.page_number if chunk.span else None
                section = chunk.span.section_title if chunk.span else None

                # Compute source reliability
                if fname not in source_scores:
                    source_scores[fname] = self.reliability_eval.evaluate_source(
                        document_filename=fname,
                        chunk_content=chunk.content,
                        document_metadata=chunk.metadata,
                        corroboration_count=doc_counts.get(fname, 1)
                    )

                # NLI Evaluation between claim and chunk content
                # Split chunk into sentences to find best matching sentence
                sentences = re.split(r"(?<=[.!?])\s+", chunk.content)
                best_nli = None

                for sent in sentences:
                    if len(sent.strip()) < 15:
                        continue
                    nli_res = self.nli.evaluate_pair(premise=sent, hypothesis=claim_text)
                    if nli_res.verdict != NLIClassificationType.NEUTRAL:
                        if not best_nli or nli_res.confidence > best_nli.confidence:
                            best_nli = (nli_res, sent)

                if best_nli:
                    nli_res, best_sent = best_nli
                    cit = EvidenceCitation(
                        citation_id=f"cit-{uuid.uuid4().hex[:8]}",
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        document_filename=fname,
                        page_number=page,
                        section_title=section,
                        exact_quote=best_sent.strip(),
                        relevance_score=sc.final_score
                    )

                    if nli_res.verdict == NLIClassificationType.ENTAILMENT:
                        supporting.append(cit)
                    elif nli_res.verdict in (
                        NLIClassificationType.CONTRADICTION,
                        NLIClassificationType.PARTIAL_CONTRADICTION,
                        NLIClassificationType.DIFFERENT_CONDITIONS,
                        NLIClassificationType.TEMPORAL_DIFFERENCE
                    ):
                        contradicting.append(cit)
                        conflict_reasons.append(
                            f"[{fname}] {nli_res.verdict.value.upper()}: {nli_res.explanation}"
                        )

            has_conflict = len(contradicting) > 0
            if has_conflict and len(supporting) > 0:
                ver_status = "partially_supported"
                conf_score = 0.65
            elif has_conflict:
                ver_status = "contradicted"
                conf_score = 0.35
            elif len(supporting) > 0:
                ver_status = "supported"
                conf_score = min(1.0, 0.75 + len(supporting) * 0.1)
            else:
                ver_status = "insufficient_evidence"
                conf_score = 0.0

            grouped = GroupedClaimEvidence(
                claim_id=str(uuid.uuid4()),
                statement=claim_text,
                supporting_citations=supporting,
                contradicting_citations=contradicting,
                conflict_explanation=" | ".join(conflict_reasons) if conflict_reasons else None,
                has_conflict=has_conflict,
                verification_status=ver_status,
                confidence_score=round(conf_score, 2),
                source_qualities=source_scores
            )
            grouped_results.append(grouped)

        return grouped_results
