"""
Unit tests for Chart and Figure Metadata Extractor (Phase 8).
"""
import pytest
from app.infrastructure.parsers.chart_figure_extractor import ChartFigureExtractor


def test_chart_and_figure_metadata_extraction():
    extractor = ChartFigureExtractor()
    text = """
<!-- PAGE_12 -->
Figure 3: Multi-Head Attention Scaling and Latency
The chart illustrates performance over sequence length from 128 to 4096 tokens.
On the vertical axis, the plot measures latency in milliseconds, reaching 45ms at peak.
The visible values show scaling at 91.2% efficiency with 1.4B parameters.
"""
    figures = extractor.extract_figures_and_charts(text, default_page=1)

    assert len(figures) == 1
    fig = figures[0]
    assert "Figure 3" in fig.caption
    assert fig.source_page == 12
    assert fig.figure_type in ("figure", "chart")
    assert "45ms" in fig.visible_values or "91.2%" in fig.visible_values
    assert fig.x_axis_label is not None or "sequence" in fig.explanatory_text
    assert fig.y_axis_label is not None or "latency" in fig.explanatory_text
