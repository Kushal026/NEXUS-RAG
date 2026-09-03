"""
Chart and Figure Metadata Extractor for NEXUS-RAG Multimodal Evidence Engine (Phase 8).
Extracts chart titles, figure captions, axes (X/Y), visible values, and surrounding explanatory text.
"""
from typing import List, Optional, Dict, Any
import re
import uuid
from app.domain.models import ChartFigureData
from app.core.logging import logger


class ChartFigureExtractor:
    """Extracts structured figure and chart intelligence from document text."""

    FIGURE_PATTERNS = [
        r"(?:Figure|Fig\.|Chart|Diagram|Plot|Illustration)\s+(\d+(?:\.\d+)?)\s*[:\-–]\s*([^\n\.\;]+)",
        r"(?:Architecture\s+Overview|System\s+Diagram)\s*[:\-–]\s*([^\n\.\;]+)"
    ]

    AXIS_PATTERNS = {
        "x_axis": [
            r"\b(?:x-axis|horizontal\s+axis|abscissa)\s*[:\-–=]\s*([^\n,;\.]+)",
            r"\b(?:x|horizontal)\s*[:\-–=]\s*([^\n,;\.]+)",
            r"\b(?:over|across|versus|vs\.?)\s+([A-Za-z0-9\-_ ]{3,25}(?:time|steps|layers|batch|tokens|epochs|depth))\b"
        ],
        "y_axis": [
            r"\b(?:y-axis|vertical\s+axis|ordinate)\s*[:\-–=]\s*([^\n,;\.]+)",
            r"\b(?:y|vertical)\s*[:\-–=]\s*([^\n,;\.]+)",
            r"\b(?:measures|measuring|plots|shows)\s+([A-Za-z0-9\-_ ]{3,25}(?:accuracy|latency|loss|throughput|bleu|rouge|f1|score|mrr))\b"
        ]
    }

    def extract_figures_and_charts(self, text: str, default_page: int = 1) -> List[ChartFigureData]:
        """Extracts all figure and chart references along with their metadata and surrounding context."""
        figures: List[ChartFigureData] = []
        current_page = default_page

        lines = text.split("\n")
        for i, line in enumerate(lines):
            # Track page markers
            page_match = re.search(r"<!--\s*PAGE_(\d+)\s*-->", line)
            if page_match:
                current_page = int(page_match.group(1))

            for pat in self.FIGURE_PATTERNS:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    full_caption = line.strip(" #*")
                    fig_label = m.group(0).strip(" #*")
                    fig_title = m.group(m.lastindex).strip(" #*") if m.lastindex else fig_label

                    # Determine figure type
                    lower_line = line.lower()
                    if "chart" in lower_line or "plot" in lower_line or "graph" in lower_line:
                        fig_type = "chart"
                    elif "diagram" in lower_line or "architecture" in lower_line or "flowchart" in lower_line:
                        fig_type = "diagram"
                    elif "scan" in lower_line:
                        fig_type = "scan"
                    else:
                        fig_type = "figure"

                    # Look at surrounding context window (+/- 3 lines)
                    context_lines = lines[max(0, i - 1):min(len(lines), i + 4)]
                    context_text = " ".join([l.strip(" #*") for l in context_lines if l.strip()])

                    # Extract X and Y axis labels
                    x_label = self._extract_axis(context_text, "x_axis")
                    y_label = self._extract_axis(context_text, "y_axis")

                    # Extract visible values / metrics
                    values = re.findall(r"\b\d+(?:\.\d+)?(?:\%|ms|s|B|M|k|x|G|MB|GB)?\b", context_text)
                    filtered_values = [v for v in values if len(v) > 1][:6]

                    fig_id = f"fig-{uuid.uuid4().hex[:8]}"
                    figures.append(ChartFigureData(
                        figure_id=fig_id,
                        title=fig_title,
                        caption=full_caption,
                        figure_type=fig_type,
                        x_axis_label=x_label,
                        y_axis_label=y_label,
                        visible_values=filtered_values,
                        explanatory_text=context_text,
                        source_page=current_page
                    ))
                    break

        return figures

    def _extract_axis(self, context: str, axis_type: str) -> Optional[str]:
        for pat in self.AXIS_PATTERNS[axis_type]:
            m = re.search(pat, context, re.IGNORECASE)
            if m:
                return m.group(1).strip(" \"'()")
        return None
