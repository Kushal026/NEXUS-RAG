"""
Structured Table Extractor for NEXUS-RAG Multimodal Evidence Engine (Phase 8).
Parses tables from Markdown, HTML, CSV, DOCX, and PDF text with headers, rows, and source page tracking.
"""
from typing import List, Optional, Dict, Any
import re
import uuid
import csv
import io
from app.domain.models import TableData
from app.core.logging import logger


class TableExtractor:
    """Extracts structured table representations from raw document text and formats."""

    def extract_markdown_tables(self, text: str, default_page: int = 1) -> List[TableData]:
        """Extracts markdown table blocks (| col1 | col2 | ...)."""
        tables: List[TableData] = []
        current_page = default_page

        lines = text.split("\n")
        table_lines: List[str] = []
        table_caption = None

        for line in lines:
            # Track page markers
            page_match = re.search(r"<!--\s*PAGE_(\d+)\s*-->", line)
            if page_match:
                current_page = int(page_match.group(1))

            # Look for captions right before table
            cap_match = re.search(r"(?:Table\s+(\d+(?:\.\d+)?)\s*[:\-–]\s*)(.+)", line, re.IGNORECASE)
            if cap_match:
                table_caption = line.strip(" #*")

            if "|" in line and not line.strip().startswith("```"):
                table_lines.append(line.strip())
            else:
                if len(table_lines) >= 2:
                    table = self._parse_table_lines(table_lines, table_caption, current_page)
                    if table:
                        tables.append(table)
                    table_caption = None
                table_lines = []
                if not cap_match and line.strip() and not line.strip().startswith("<!--"):
                    table_caption = None


        if len(table_lines) >= 2:
            table = self._parse_table_lines(table_lines, table_caption, current_page)
            if table:
                tables.append(table)

        return tables

    def _parse_table_lines(self, lines: List[str], caption: Optional[str], page: int) -> Optional[TableData]:
        """Parses a block of table pipe lines into headers and row values."""
        raw_rows = []
        for l in lines:
            if re.match(r"^\|?\s*[\:\-\s\|]+\s*\|?$", l):
                continue  # Skip separator line like |---|---|
            cells = [c.strip() for c in l.strip("|").split("|")]
            if len(cells) >= 2 and any(c for c in cells):
                raw_rows.append(cells)

        if len(raw_rows) < 1:
            return None

        headers = raw_rows[0]
        rows = raw_rows[1:] if len(raw_rows) > 1 else []

        # Generate clean markdown representation
        header_row = "| " + " | ".join(headers) + " |"
        sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        body_rows = ["| " + " | ".join(r + [""] * (len(headers) - len(r))) + " |" for r in rows]
        md_repr = "\n".join([header_row, sep_row] + body_rows)

        return TableData(
            table_id=f"tbl-{uuid.uuid4().hex[:8]}",
            headers=headers,
            rows=rows,
            num_rows=len(rows),
            num_cols=len(headers),
            caption=caption or f"Table (Page {page})",
            source_page=page,
            markdown_repr=md_repr
        )

    def extract_from_csv(self, csv_content: str, filename: str = "data.csv") -> TableData:
        """Parses raw CSV string into TableData."""
        reader = csv.reader(io.StringIO(csv_content.strip()))
        rows_list = list(reader)
        if not rows_list:
            return TableData(
                table_id=f"tbl-{uuid.uuid4().hex[:8]}",
                headers=[],
                rows=[],
                num_rows=0,
                num_cols=0,
                caption=filename,
                source_page=1,
                markdown_repr=""
            )

        headers = rows_list[0]
        data_rows = rows_list[1:]

        header_row = "| " + " | ".join(headers) + " |"
        sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        body_rows = ["| " + " | ".join(r + [""] * (len(headers) - len(r))) + " |" for r in data_rows[:20]]
        md_repr = "\n".join([header_row, sep_row] + body_rows)

        return TableData(
            table_id=f"tbl-{uuid.uuid4().hex[:8]}",
            headers=headers,
            rows=data_rows,
            num_rows=len(data_rows),
            num_cols=len(headers),
            caption=f"Dataset Table ({filename})",
            source_page=1,
            markdown_repr=md_repr
        )
