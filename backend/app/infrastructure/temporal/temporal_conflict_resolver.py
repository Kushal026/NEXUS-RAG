"""
Temporal Conflict Resolver classifying differences between claims into Genuine Contradictions,
Version Supersessions, and Chronological Temporal Evolutions.
"""
from typing import Optional, Dict, Any
import re
from app.domain.models import TemporalConflictType, TemporalConflictResult
from app.core.logging import logger


class TemporalConflictResolver:
    """Classifies temporal divergences to avoid confusing historical evolution with contradictions."""

    @staticmethod
    def _extract_year(text: Optional[str]) -> Optional[int]:
        if not text:
            return None
        m = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        return int(m.group(1)) if m else None

    @staticmethod
    def _extract_version_num(text: Optional[str]) -> Optional[float]:
        if not text:
            return None
        # Match "v1.2", "version 2", or standalone version "1.0.0", "2.0"
        m = re.search(r"(?:(?:v|version)\s*)?([0-9]+(?:\.[0-9]+)*)", text, flags=re.IGNORECASE)
        if m:
            parts = m.group(1).split(".")
            major = parts[0]
            minor = parts[1] if len(parts) > 1 else "0"
            return float(f"{major}.{minor}")
        return None

    def resolve_conflict(
        self,
        claim_a: str,
        claim_b: str,
        timestamp_a: Optional[str] = None,
        timestamp_b: Optional[str] = None,
        doc_a: Optional[str] = None,
        doc_b: Optional[str] = None,
        version_a: Optional[str] = None,
        version_b: Optional[str] = None
    ) -> TemporalConflictResult:
        """Determines whether divergent claims represent a Version Change, Temporal Evolution, or Genuine Contradiction."""
        year_a = self._extract_year(timestamp_a) or self._extract_year(doc_a) or self._extract_year(claim_a)
        year_b = self._extract_year(timestamp_b) or self._extract_year(doc_b) or self._extract_year(claim_b)

        v_a = self._extract_version_num(version_a) or self._extract_version_num(doc_a)
        v_b = self._extract_version_num(version_b) or self._extract_version_num(doc_b)

        # 1. Version Supersession Check
        if v_a is not None and v_b is not None and v_a != v_b:
            newer_v = max(v_a, v_b)
            older_v = min(v_a, v_b)
            newer_doc = doc_b if newer_v == v_b else doc_a
            explanation = (
                f"Version Change: {newer_doc} (v{newer_v}) supersedes older specification (v{older_v}). "
                f"The newer version represents the current active specification."
            )
            return TemporalConflictResult(
                claim_a=claim_a,
                claim_b=claim_b,
                timestamp_a=timestamp_a,
                timestamp_b=timestamp_b,
                document_a=doc_a,
                document_b=doc_b,
                conflict_type=TemporalConflictType.VERSION_CHANGE,
                explanation=explanation,
                confidence=0.95
            )

        # 2. Chronological Temporal Evolution Check
        if year_a is not None and year_b is not None and year_a != year_b:
            earlier_yr = min(year_a, year_b)
            later_yr = max(year_a, year_b)
            explanation = (
                f"Temporal Evolution: The state described in {earlier_yr} was historically accurate for that epoch, "
                f"but subsequently evolved by {later_yr}. These states are not in contradiction; they represent chronological progress."
            )
            return TemporalConflictResult(
                claim_a=claim_a,
                claim_b=claim_b,
                timestamp_a=timestamp_a,
                timestamp_b=timestamp_b,
                document_a=doc_a,
                document_b=doc_b,
                conflict_type=TemporalConflictType.TEMPORAL_EVOLUTION,
                explanation=explanation,
                confidence=0.92
            )

        # 3. Same Timestamp / No Temporal Separation -> Genuine Contradiction
        explanation = (
            f"Genuine Contradiction: Conflicting assertions made for the same epoch ({year_a or 'unspecified'}) "
            f"without documented version supersession."
        )
        return TemporalConflictResult(
            claim_a=claim_a,
            claim_b=claim_b,
            timestamp_a=timestamp_a,
            timestamp_b=timestamp_b,
            document_a=doc_a,
            document_b=doc_b,
            conflict_type=TemporalConflictType.GENUINE_CONTRADICTION,
            explanation=explanation,
            confidence=0.88
        )
