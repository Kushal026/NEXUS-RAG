"""
Temporal Extractor parsing point-in-time dates, chronological epochs, and temporal intents.
"""
from typing import Optional, Tuple, Dict, Any
import re
from datetime import datetime
from app.domain.models import TemporalFilter
from app.core.logging import logger


class TemporalExtractor:
    """Extracts temporal boundaries, dates, and version constraints from text & queries."""

    YEAR_PATTERN = r"\b(19\d{2}|20\d{2})\b"
    ISO_DATE_PATTERN = r"\b(\d{4}-\d{2}-\d{2})\b"
    BETWEEN_PATTERN = r"\bbetween\s+(\d{4}(?:-\d{2}-\d{2})?)\s+and\s+(\d{4}(?:-\d{2}-\d{2})?)\b"
    FROM_TO_PATTERN = r"\bfrom\s+(\d{4}(?:-\d{2}-\d{2})?)\s+to\s+(\d{4}(?:-\d{2}-\d{2})?)\b"
    AS_OF_PATTERN = r"\b(?:as of|in|during|for year)\s+(\d{4}(?:-\d{2}-\d{2})?)\b"
    SINCE_AFTER_PATTERN = r"\b(?:since|after)\s+(\d{4}(?:-\d{2}-\d{2})?)\b"
    VERSION_PATTERN = r"\b(?:v|version)\s*([0-9]+(?:\.[0-9]+)*)\b"

    def extract_temporal_filter(self, query: str) -> Tuple[Optional[TemporalFilter], str]:
        """Parses query string to extract TemporalFilter and returns (filter, cleaned_query)."""
        q_lower = query.lower()
        cleaned_q = query
        as_of = None
        start_d = None
        end_d = None
        version = None
        latest_only = False

        # 1. Check for "latest" / "current" / "newest" / "recent"
        if re.search(r"\b(latest|current|newest|most recent|up-to-date)\b", q_lower):
            latest_only = True
            cleaned_q = re.sub(r"\b(latest|current|newest|most recent|up-to-date)\b", "", cleaned_q, flags=re.IGNORECASE).strip()

        # 2. Check for "between X and Y" or "from X to Y"
        between_m = re.search(self.BETWEEN_PATTERN, q_lower)
        from_to_m = re.search(self.FROM_TO_PATTERN, q_lower)
        if between_m:
            start_d = between_m.group(1)
            end_d = between_m.group(2)
            cleaned_q = re.sub(self.BETWEEN_PATTERN, "", cleaned_q, flags=re.IGNORECASE).strip()
        elif from_to_m:
            start_d = from_to_m.group(1)
            end_d = from_to_m.group(2)
            cleaned_q = re.sub(self.FROM_TO_PATTERN, "", cleaned_q, flags=re.IGNORECASE).strip()

        # 3. Check for "as of X" / "in 2023"
        as_of_m = re.search(self.AS_OF_PATTERN, q_lower)
        if as_of_m and not (start_d and end_d):
            as_of = as_of_m.group(1)
            cleaned_q = re.sub(self.AS_OF_PATTERN, "", cleaned_q, flags=re.IGNORECASE).strip()

        # 4. Check for "since/after X"
        after_m = re.search(self.SINCE_AFTER_PATTERN, q_lower)
        if after_m and not start_d:
            start_d = after_m.group(1)
            cleaned_q = re.sub(self.SINCE_AFTER_PATTERN, "", cleaned_q, flags=re.IGNORECASE).strip()

        # 5. Check for explicit version (e.g. "v1.0.0", "version 2")
        version_m = re.search(self.VERSION_PATTERN, q_lower)
        if version_m:
            version = version_m.group(1)
            cleaned_q = re.sub(self.VERSION_PATTERN, "", cleaned_q, flags=re.IGNORECASE).strip()

        # Clean excess spaces
        cleaned_q = re.sub(r"\s+", " ", cleaned_q).strip()

        if as_of or start_d or end_d or version or latest_only:
            t_filter = TemporalFilter(
                as_of_date=as_of,
                start_date=start_d,
                end_date=end_d,
                version=version,
                latest_only=latest_only
            )
            logger.info(f"Extracted TemporalFilter from query: as_of={as_of}, range=[{start_d}..{end_d}], ver={version}, latest={latest_only}")
            return t_filter, cleaned_q

        return None, query

    def extract_document_dates(self, content: str, filename: str) -> Dict[str, Any]:
        """Infers document creation/validity year and version from content and filename."""
        dates = {}
        # Version from filename (e.g., specs_v2.md -> 2.0.0)
        v_match = re.search(r"[_\-\.](v[0-9]+(?:\.[0-9]+)*)", filename, flags=re.IGNORECASE)
        if v_match:
            raw_v = v_match.group(1).lstrip("vV")
            dates["version"] = f"{raw_v}.0.0" if "." not in raw_v else raw_v
        else:
            dates["version"] = "1.0.0"

        # Year from filename (e.g. 2023_quantum.md)
        fn_year = re.search(r"(19\d{2}|20\d{2})", filename)
        if fn_year:
            year_val = fn_year.group(1)
            dates["published_at"] = f"{year_val}-01-01T00:00:00"
            dates["valid_from"] = f"{year_val}-01-01T00:00:00"

        # Year from content header
        if "published_at" not in dates:
            content_year = re.search(r"(?:Published|Date|Release|Year):\s*(19\d{2}|20\d{2})", content, flags=re.IGNORECASE)
            if content_year:
                year_val = content_year.group(1)
                dates["published_at"] = f"{year_val}-01-01T00:00:00"
                dates["valid_from"] = f"{year_val}-01-01T00:00:00"

        return dates
