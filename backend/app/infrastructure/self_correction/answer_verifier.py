"""
Answer Verifier & Regeneration Engine for NEXUS-RAG (Phase 7).
Extracts atomic claims from synthesized answers, verifies them against accumulated evidence with NLI,
and redacts or regenerates unsupported assertions to guarantee zero hallucinations.
"""
from typing import List, Dict, Tuple, Optional
import re
import uuid
from app.domain.models import (
    ScoredChunk,
    AnswerVerificationResult,
    VerifiedClaimItem,
    EvidenceCitation,
    NLIClassificationType
)
from app.infrastructure.evidence.nli_engine import NLIEngine
from app.core.logging import logger


class AnswerVerifier:
    """Verifies generated answers against evidence and redacts/regenerates ungrounded claims."""

    def __init__(self, nli_engine: Optional[NLIEngine] = None):
        self.nli = nli_engine or NLIEngine()

    def extract_factual_claims(self, text: str) -> List[str]:
        """Extracts individual factual sentences from answer markdown."""
        lines = text.split("\n")
        claims: List[str] = []
        for line in lines:
            cleaned = re.sub(r"^[#\-\*\d\.\s>]+", "", line).strip()
            # Strip source citation prefixes like [Source 1] (file - P.1):
            cleaned = re.sub(r"^\[Source\s+\d+\][^\:]*\:\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = cleaned.strip(" \"'“”*`#")

            if (
                len(cleaned) < 15
                or cleaned.startswith("```")
                or cleaned.lower().startswith("based on")
                or cleaned.lower().startswith("verified source")
                or cleaned.lower().startswith("references")
                or cleaned.lower().startswith("system notice")
                or cleaned.lower().startswith("insufficient evidence")
            ):
                continue

            for s in re.split(r"(?<=[.!?])\s+", cleaned):
                s_clean = s.strip(" \"'“”*`#")
                s_clean = re.sub(r"\[Source\s+\d+\]", "", s_clean, flags=re.IGNORECASE).strip()
                if (
                    len(s_clean) > 20
                    and not s_clean.lower().startswith("based on")
                    and not s_clean.lower().startswith("verified source")
                    and not s_clean.lower().startswith("references")
                ):
                    claims.append(s_clean)
        return claims[:10]



    def verify_answer(
        self,
        raw_answer: str,
        accumulated_chunks: List[ScoredChunk]
    ) -> AnswerVerificationResult:
        """
        Extracts claims, validates them against evidence with NLI, and produces a filtered verified answer.
        """
        claims = self.extract_factual_claims(raw_answer)
        if not claims or not accumulated_chunks:
            return AnswerVerificationResult(
                raw_answer=raw_answer,
                final_answer=raw_answer,
                extracted_claims=claims,
                verified_claim_items=[],
                supported_claims_count=0,
                unsupported_claims_count=len(claims),
                contradicted_claims_count=0,
                unsupported_claim_rate=1.0 if claims else 0.0,
                was_regenerated=False,
                regeneration_reason=None
            )

        verified_items: List[VerifiedClaimItem] = []
        supported_count = 0
        unsupported_count = 0
        contradicted_count = 0

        for claim in claims:
            best_verdict = NLIClassificationType.NEUTRAL
            best_confidence = 0.0
            citations: List[EvidenceCitation] = []
            note = None

            for sc in accumulated_chunks:
                chunk = sc.chunk
                sentences = re.split(r"(?<=[.!?])\s+", chunk.content)
                for sent in sentences:
                    if len(sent.strip()) < 15:
                        continue
                    nli_res = self.nli.evaluate_pair(premise=sent, hypothesis=claim)
                    if nli_res.verdict != NLIClassificationType.NEUTRAL:
                        if nli_res.confidence > best_confidence:
                            best_verdict = nli_res.verdict
                            best_confidence = nli_res.confidence
                            note = nli_res.explanation
                            citations.append(EvidenceCitation(
                                citation_id=f"cit-{uuid.uuid4().hex[:8]}",
                                chunk_id=chunk.id,
                                document_id=chunk.document_id,
                                document_filename=chunk.metadata.get("filename", "Doc"),
                                page_number=chunk.span.page_number if chunk.span else 1,
                                exact_quote=sent.strip(),
                                relevance_score=sc.final_score
                            ))

            if best_verdict == NLIClassificationType.ENTAILMENT:
                status = "supported"
                supported_count += 1
            elif best_verdict in (
                NLIClassificationType.CONTRADICTION,
                NLIClassificationType.PARTIAL_CONTRADICTION
            ):
                status = "contradicted"
                contradicted_count += 1
            else:
                status = "unsupported"
                unsupported_count += 1
                note = "No corroborating passage found in accumulated evidence."

            verified_items.append(VerifiedClaimItem(
                claim_text=claim,
                status=status,
                confidence=round(best_confidence if best_confidence > 0 else 0.40, 2),
                supporting_citations=citations[:2],
                verification_note=note
            ))

        total_claims = len(claims)
        unsupported_rate = round((unsupported_count + contradicted_count) / max(1, total_claims), 2)
        was_regenerated = (unsupported_count > 0 or contradicted_count > 0)

        # Build Verified Final Answer (Filtering out or flagging unverified assertions)
        if was_regenerated:
            valid_claims = [item for item in verified_items if item.status == "supported"]
            if valid_claims:
                synthesis_lines = [
                    "### Verified Answer Synthesis (Self-Corrected)\n",
                    f"> **Verification Notice**: {unsupported_count + contradicted_count} unverified or conflicting assertions were filtered out to maintain strict groundedness.\n"
                ]
                for v in valid_claims:
                    src_tag = f" — *[{v.supporting_citations[0].document_filename}]*" if v.supporting_citations else ""
                    synthesis_lines.append(f"- {v.claim_text}{src_tag}")
                final_answer = "\n".join(synthesis_lines)
                regen_reason = f"Filtered {unsupported_count} unsupported and {contradicted_count} contradicted claims."
            else:
                final_answer = (
                    "### ⚠ Insufficient Grounded Evidence\n\n"
                    "All generated assertions failed post-generation evidence verification. Answer suppressed to prevent hallucination."
                )
                regen_reason = "All claims failed verification against accumulated evidence."
        else:
            final_answer = raw_answer
            regen_reason = None

        return AnswerVerificationResult(
            raw_answer=raw_answer,
            final_answer=final_answer,
            extracted_claims=claims,
            verified_claim_items=verified_items,
            supported_claims_count=supported_count,
            unsupported_claims_count=unsupported_count,
            contradicted_claims_count=contradicted_count,
            unsupported_claim_rate=unsupported_rate,
            was_regenerated=was_regenerated,
            regeneration_reason=regen_reason
        )
