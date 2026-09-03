"""
Parser factory for routing documents to appropriate parser based on extension / MIME.
"""
from typing import Dict, Type
from pathlib import Path
from app.domain.interfaces import BaseParser
from app.infrastructure.parsers.pdf_parser import PDFParser
from app.infrastructure.parsers.docx_parser import DOCXParser
from app.infrastructure.parsers.text_parser import PlainTextParser, HTMLParser, CSVParser
from app.core.logging import logger


class ParserFactory:
    """Factory to instantiate and retrieve document parsers."""
    
    _parsers: Dict[str, BaseParser] = {
        "pdf": PDFParser(),
        "docx": DOCXParser(),
        "txt": PlainTextParser(),
        "md": PlainTextParser(),
        "markdown": PlainTextParser(),
        "html": HTMLParser(),
        "htm": HTMLParser(),
        "csv": CSVParser(),
        "json": PlainTextParser(),
    }

    @classmethod
    def get_parser(cls, filename: str) -> BaseParser:
        ext = Path(filename).suffix.lower().lstrip(".")
        if not ext:
            return cls._parsers["txt"]
        
        parser = cls._parsers.get(ext)
        if not parser:
            logger.warning(f"No specific parser for extension '.{ext}', falling back to PlainTextParser.")
            return cls._parsers["txt"]
        return parser

    @classmethod
    def supported_extensions(cls) -> list[str]:
        return list(cls._parsers.keys())
