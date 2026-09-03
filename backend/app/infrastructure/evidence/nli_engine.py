"""
Natural Language Inference & Contradiction Detection Engine for NEXUS-RAG (Phase 6).
Evaluates agreement, direct contradiction, partial contradiction, condition discrepancies, and temporal drift.
"""
from typing import Dict, List, Tuple, Optional, Set, Any
import re
from app.domain.models import NLIClassificationType, NLIResult
from app.core.logging import logger


class NLIEngine:
    """Structured deterministic Natural Language Inference engine for evidence analysis."""

    NEGATION_WORDS = {"not", "never", "no", "cannot", "hardly", "barely", "fails", "failed", "unable", "without", "degrades", "inferior", "lacks"}
    POSITIVE_WORDS = {"outperforms", "improves", "superior", "beats", "surpasses", "exceeds", "achieves", "capable", "supports", "enables"}

    DATASET_PATTERNS = [
        r"\b(?:GLUE|SuperGLUE|SQuAD|ImageNet|MS\s+MARCO|HotpotQA|BEIR|MMLU|GSM8K|HumanEval|TriviaQA)\b",
        r"\b(?:BLEU|ROUGE|Accuracy|Precision|Recall|F1|Latency|Throughput|MRR|NDCG)\b"
    ]

    def _extract_numbers_and_percentages(self, text: str) -> List[Tuple[float, str]]:
        """Extracts numerical quantities and percentages from text."""
        results: List[Tuple[float, str]] = []
        # Match percentages e.g. 91%, 87.5%
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", text):
            try:
                results.append((float(m.group(1)), f"{m.group(1)}%"))
            except ValueError:
                pass

        # Match general numbers e.g. 91.5, 0.88, 100
        for m in re.finditer(r"\b(\d+(?:\.\d+)?)\b", text):
            try:
                val = float(m.group(1))
                val_str = m.group(1)
                if not any(v == val for v, _ in results):
                    results.append((val, val_str))
            except ValueError:
                pass

        return results

    def _extract_conditions(self, text: str) -> List[str]:
        """Extracts evaluation conditions such as benchmarks, datasets, or environments."""
        conditions: List[str] = []
        for pat in self.DATASET_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                conditions.append(m.group(0).strip())

        # Match 'on <dataset>' or 'using <method>'
        for m in re.finditer(r"\b(?:on|using|with|under)\s+([A-Z][a-zA-Z0-9\-_]+(?:\s+[A-Z][a-zA-Z0-9\-_]+)?)\b", text):
            cond = m.group(1).strip()
            if cond not in conditions and len(cond) > 2:
                conditions.append(cond)

        return conditions

    def _extract_temporal_markers(self, text: str) -> List[str]:
        """Extracts year or version markers."""
        return re.findall(r"\b(?:19\d{2}|20\d{2}|v[0-9]+(?:\.[0-9]+)*)\b", text)

    def evaluate_pair(self, premise: str, hypothesis: str) -> NLIResult:
        """
        Evaluates the NLI relationship between premise (Evidence A) and hypothesis (Evidence B).
        """
        p_clean = premise.strip()
        h_clean = hypothesis.strip()

        if not p_clean or not h_clean:
            return NLIResult(
                premise=premise,
                hypothesis=hypothesis,
                verdict=NLIClassificationType.NEUTRAL,
                confidence=0.0,
                explanation="Empty text provided."
            )

        p_nums = self._extract_numbers_and_percentages(p_clean)
        h_nums = self._extract_numbers_and_percentages(h_clean)

        p_conds = self._extract_conditions(p_clean)
        h_conds = self._extract_conditions(h_clean)

        p_time = self._extract_temporal_markers(p_clean)
        h_time = self._extract_temporal_markers(h_clean)

        p_words = set(re.findall(r"\w+", p_clean.lower()))
        h_words = set(re.findall(r"\w+", h_clean.lower()))

        # Shared content vocabulary (excluding stopwords)
        stopwords = {"the", "is", "a", "an", "and", "or", "to", "in", "of", "for", "with", "at", "by", "on", "this", "that", "it", "are", "was", "were"}
        shared_words = (p_words & h_words) - stopwords
        content_overlap = len(shared_words) / max(1, min(len(p_words - stopwords), len(h_words - stopwords)))

        p_has_neg = bool(p_words & self.NEGATION_WORDS)
        h_has_neg = bool(h_words & self.NEGATION_WORDS)
        polarity_mismatch = (p_has_neg != h_has_neg)

        # 1. Check for Temporal Differences (e.g. 2022 vs 2024 or v1 vs v2)
        if p_time and h_time and p_time != h_time and content_overlap > 0.3:
            return NLIResult(
                premise=premise,
                hypothesis=hypothesis,
                verdict=NLIClassificationType.TEMPORAL_DIFFERENCE,
                confidence=0.92,
                explanation=f"Statements reflect temporal progression across epochs ({', '.join(p_time)} vs {', '.join(h_time)}).",
                condition_a=f"Period: {', '.join(p_time)}",
                condition_b=f"Period: {', '.join(h_time)}"
            )

        # 2. Check for Different Conditions / Datasets (e.g. 91% on GLUE vs 87% on SQuAD)
        if p_conds and h_conds and set(p_conds) != set(h_conds) and content_overlap > 0.25:
            cond_a = ", ".join(p_conds)
            cond_b = ", ".join(h_conds)
            num_diff = f"{p_nums[0][1]} vs {h_nums[0][1]}" if p_nums and h_nums else None
            return NLIResult(
                premise=premise,
                hypothesis=hypothesis,
                verdict=NLIClassificationType.DIFFERENT_CONDITIONS,
                confidence=0.90,
                explanation=f"Discrepancy explained by differing evaluation conditions/datasets ({cond_a} vs {cond_b}).",
                condition_a=cond_a,
                condition_b=cond_b,
                metric_diff=num_diff
            )

        # 3. Check for Direct Numerical or Attribute Contradictions
        if p_nums and h_nums and content_overlap > 0.3:
            p_val = p_nums[0][0]
            h_val = h_nums[0][0]
            if abs(p_val - h_val) > 0.01:
                return NLIResult(
                    premise=premise,
                    hypothesis=hypothesis,
                    verdict=NLIClassificationType.CONTRADICTION,
                    confidence=0.95,
                    explanation=f"Direct numerical contradiction on same target: '{p_nums[0][1]}' vs '{h_nums[0][1]}'.",
                    metric_diff=f"{p_nums[0][1]} != {h_nums[0][1]}"
                )

        # 4. Check for Polarity / Directional Contradiction
        if polarity_mismatch and content_overlap > 0.45:
            return NLIResult(
                premise=premise,
                hypothesis=hypothesis,
                verdict=NLIClassificationType.CONTRADICTION,
                confidence=0.88,
                explanation="Direct assertion conflict: one statement asserts an outcome while the other negates or refutes it."
            )

        # 5. Check for Partial Contradiction
        if polarity_mismatch and content_overlap > 0.25:
            return NLIResult(
                premise=premise,
                hypothesis=hypothesis,
                verdict=NLIClassificationType.PARTIAL_CONTRADICTION,
                confidence=0.78,
                explanation="Partial contradiction: overlapping subject matter with conflicting directional qualifiers."
            )

        # 6. Check for Entailment / High Agreement
        if content_overlap >= 0.5 and not polarity_mismatch:
            # If both have matching numbers
            if p_nums and h_nums and abs(p_nums[0][0] - h_nums[0][0]) < 0.01:
                return NLIResult(
                    premise=premise,
                    hypothesis=hypothesis,
                    verdict=NLIClassificationType.ENTAILMENT,
                    confidence=0.96,
                    explanation="Direct mutual agreement: both statements substantiate the exact same metrics and claim."
                )
            return NLIResult(
                premise=premise,
                hypothesis=hypothesis,
                verdict=NLIClassificationType.ENTAILMENT,
                confidence=round(min(0.95, 0.6 + content_overlap * 0.4), 2),
                explanation="Substantive agreement: the evidence statements mutually support the underlying assertion."
            )

        # 7. Default Neutral
        return NLIResult(
            premise=premise,
            hypothesis=hypothesis,
            verdict=NLIClassificationType.NEUTRAL,
            confidence=0.60,
            explanation="Statements discuss different topics without direct support or contradiction."
        )
