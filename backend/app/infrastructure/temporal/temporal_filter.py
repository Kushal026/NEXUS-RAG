"""
Temporal Filter Engine evaluating point-in-time, date-range, and latest-version validity constraints.
"""
from typing import Optional, Dict, Any
import re
from datetime import datetime
from app.domain.models import DocumentChunk, TemporalFilter
from app.core.logging import logger


class TemporalFilterEngine:
    """Evaluates temporal validity predicates on chunks and documents."""

    @staticmethod
    def _parse_year_or_date(d_val: Any) -> Optional[int]:
        if not d_val:
            return None
        if isinstance(d_val, datetime):
            return d_val.year
        s = str(d_val)
        y_m = re.search(r"\b(19\d{2}|20\d{2})\b", s)
        return int(y_m.group(1)) if y_m else None

    @classmethod
    def matches_chunk(cls, chunk: DocumentChunk, t_filter: Optional[TemporalFilter]) -> bool:
        if not t_filter:
            return True

        meta = chunk.metadata or {}
        chunk_is_latest = chunk.is_latest if chunk.is_latest is not None else meta.get("is_latest", True)
        chunk_version = chunk.version or meta.get("version", "1.0.0")

        # 1. Latest-Only filter
        if t_filter.latest_only and not chunk_is_latest:
            return False

        # 2. Version match filter
        if t_filter.version:
            target_v = t_filter.version.lstrip("vV")
            c_v = chunk_version.lstrip("vV")
            if not c_v.startswith(target_v):
                return False

        # Extract validity years
        vf_year = cls._parse_year_or_date(chunk.valid_from or meta.get("valid_from") or meta.get("published_at"))
        vu_year = cls._parse_year_or_date(chunk.valid_until or meta.get("valid_until"))

        # 3. As-Of Point-in-time filter (e.g. "What was true in 2023?")
        if t_filter.as_of_date:
            as_of_year = cls._parse_year_or_date(t_filter.as_of_date)
            if as_of_year:
                # If chunk has valid_from, it must be <= as_of_year
                if vf_year and vf_year > as_of_year:
                    return False
                # If chunk has valid_until, it must be >= as_of_year
                if vu_year and vu_year < as_of_year:
                    return False

        # 4. Date Range filter (e.g. "between 2024 and 2026")
        if t_filter.start_date:
            start_year = cls._parse_year_or_date(t_filter.start_date)
            if start_year and vu_year and vu_year < start_year:
                return False

        if t_filter.end_date:
            end_year = cls._parse_year_or_date(t_filter.end_date)
            if end_year and vf_year and vf_year > end_year:
                return False

        return True
