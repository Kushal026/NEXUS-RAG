"""
PyMuPDF (fitz) parser for PDF document ingestion.
Extracts page-level text, structural markers, and metadata.
"""
from typing import Optional, Dict, Any
import fitz  # PyMuPDF
from app.domain.models import Document, DocumentMetadata
from app.core.logging import logger


class PDFParser:
    """Extracts text, pages, and metadata from PDF files."""

    def parse(self, file_content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        custom_meta = metadata or {}
        doc = fitz.open(stream=file_content, filetype="pdf")
        
        page_count = len(doc)
        text_parts = []
        
        pdf_meta = doc.metadata or {}
        title = pdf_meta.get("title") or filename
        author = pdf_meta.get("author")

        for page_idx in range(page_count):
            page = doc.load_page(page_idx)
            page_text = page.get_text("text").strip()
            if page_text:
                # Add page delimiter token to preserve structure for the chunker
                text_parts.append(f"<!-- PAGE_{page_idx + 1} -->\n{page_text}")

        full_content = "\n\n".join(text_parts)
        doc.close()

        logger.info(f"Parsed PDF '{filename}': {page_count} pages, {len(full_content)} chars.")

        return Document(
            filename=filename,
            content=full_content,
            metadata=DocumentMetadata(
                title=title,
                author=author,
                file_type="pdf",
                file_size=len(file_content),
                page_count=page_count,
                custom_metadata=custom_meta
            )
        )
