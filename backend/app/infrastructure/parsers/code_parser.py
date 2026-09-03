"""
Code Parser & Code Block Extractor for NEXUS-RAG Multimodal Evidence Engine (Phase 8).
Parses programming language files and extracts structured code blocks with syntax metadata.
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import re
import uuid
from app.domain.interfaces import BaseParser
from app.domain.models import Document, DocumentMetadata, CodeBlockData
from app.core.logging import logger


class CodeParser(BaseParser):
    """Parses source code files and extracts functions, classes, and code blocks."""

    EXTENSION_LANG_MAP = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "jsx": "javascript",
        "go": "go",
        "rs": "rust",
        "cpp": "cpp",
        "c": "c",
        "h": "c",
        "java": "java",
        "sql": "sql",
        "sh": "bash",
        "bash": "bash",
        "ps1": "powershell",
        "yaml": "yaml",
        "yml": "yaml",
        "json": "json"
    }

    def parse(self, file_content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        custom_meta = metadata or {}
        ext = Path(filename).suffix.lower().lstrip(".")
        language = self.EXTENSION_LANG_MAP.get(ext, "text")

        text = file_content.decode("utf-8", errors="replace")
        formatted_content = f"<!-- PAGE_1 -->\n```{language}\n// File: {filename}\n{text}\n```"

        logger.info(f"Parsed Code file '{filename}' ({language}): {len(text)} chars.")

        return Document(
            filename=filename,
            content=formatted_content,
            metadata=DocumentMetadata(
                title=f"Source Code: {filename}",
                author=custom_meta.get("author"),
                file_type=f"code_{language}",
                file_size=len(file_content),
                page_count=1,
                custom_attributes={
                    **custom_meta,
                    "language": language,
                    "is_code": True
                }
            )
        )


    def extract_code_blocks_from_markdown(self, text: str, default_page: int = 1) -> List[CodeBlockData]:
        """Extracts fenced code blocks (```lang ... ```) from markdown text."""
        blocks: List[CodeBlockData] = []
        current_page = default_page

        pattern = r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```"
        for m in re.finditer(pattern, text, re.DOTALL):
            lang = m.group(1).strip() or "text"
            code = m.group(2).strip()
            if len(code) > 10:
                blocks.append(CodeBlockData(
                    code_id=f"code-{uuid.uuid4().hex[:8]}",
                    language=lang,
                    code_content=code,
                    source_page=current_page
                ))

        return blocks
