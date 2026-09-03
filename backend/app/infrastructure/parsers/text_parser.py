"""
Parsers for text-based formats: Plaintext, Markdown, HTML, CSV, and JSON.
"""
from typing import Optional, Dict, Any
import csv
import io
import json
from bs4 import BeautifulSoup
from app.domain.models import Document, DocumentMetadata
from app.core.logging import logger


class PlainTextParser:
    """Parses standard UTF-8 text and markdown documents."""

    def parse(self, file_content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        custom_meta = metadata or {}
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1", errors="replace")

        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        logger.info(f"Parsed text document '{filename}': {len(text)} chars.")
        return Document(
            filename=filename,
            content=text,
            metadata=DocumentMetadata(
                title=filename,
                file_type=ext,
                file_size=len(file_content),
                custom_metadata=custom_meta
            )
        )


class HTMLParser:
    """Parses HTML documents using BeautifulSoup to extract clean text."""

    def parse(self, file_content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        custom_meta = metadata or {}
        try:
            html_text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            html_text = file_content.decode("latin-1", errors="replace")

        soup = BeautifulSoup(html_text, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style", "meta", "noscript"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else filename
        text = soup.get_text(separator="\n\n", strip=True)

        logger.info(f"Parsed HTML document '{filename}': {len(text)} chars.")
        return Document(
            filename=filename,
            content=text,
            metadata=DocumentMetadata(
                title=title,
                file_type="html",
                file_size=len(file_content),
                custom_metadata=custom_meta
            )
        )


class CSVParser:
    """Parses tabular CSV files into readable markdown table format."""

    def parse(self, file_content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        custom_meta = metadata or {}
        try:
            csv_str = file_content.decode("utf-8")
        except UnicodeDecodeError:
            csv_str = file_content.decode("latin-1", errors="replace")

        reader = csv.reader(io.StringIO(csv_str))
        rows = list(reader)
        
        if not rows:
            formatted_text = ""
        else:
            header = " | ".join(rows[0])
            divider = " | ".join(["---"] * len(rows[0]))
            data_rows = [" | ".join(r) for r in rows[1:]]
            formatted_text = f"{header}\n{divider}\n" + "\n".join(data_rows)

        logger.info(f"Parsed CSV document '{filename}': {len(rows)} rows.")
        return Document(
            filename=filename,
            content=formatted_text,
            metadata=DocumentMetadata(
                title=filename,
                file_type="csv",
                file_size=len(file_content),
                custom_metadata=custom_meta
            )
        )
