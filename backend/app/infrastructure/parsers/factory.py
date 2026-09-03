from typing import Dict, Type
from pathlib import Path
from app.domain.interfaces import BaseParser
from app.infrastructure.parsers.pdf_parser import PDFParser
from app.infrastructure.parsers.docx_parser import DOCXParser
from app.infrastructure.parsers.text_parser import PlainTextParser, HTMLParser, CSVParser
from app.infrastructure.parsers.image_ocr_parser import ImageOCRParser
from app.infrastructure.parsers.code_parser import CodeParser
from app.core.logging import logger


class ParserFactory:
    """Factory to instantiate and retrieve document parsers for all modalities."""

    _pdf_parser = PDFParser()
    _docx_parser = DOCXParser()
    _text_parser = PlainTextParser()
    _html_parser = HTMLParser()
    _csv_parser = CSVParser()
    _image_parser = ImageOCRParser()
    _code_parser = CodeParser()

    _parsers: Dict[str, BaseParser] = {
        # Documents
        "pdf": _pdf_parser,
        "docx": _docx_parser,
        "txt": _text_parser,
        "md": _text_parser,
        "markdown": _text_parser,
        "html": _html_parser,
        "htm": _html_parser,
        "csv": _csv_parser,
        # Code
        "py": _code_parser,
        "ts": _code_parser,
        "tsx": _code_parser,
        "js": _code_parser,
        "jsx": _code_parser,
        "go": _code_parser,
        "rs": _code_parser,
        "cpp": _code_parser,
        "c": _code_parser,
        "h": _code_parser,
        "java": _code_parser,
        "sql": _code_parser,
        "sh": _code_parser,
        "bash": _code_parser,
        "ps1": _code_parser,
        "yaml": _code_parser,
        "yml": _code_parser,
        "json": _code_parser,
        # Images & Scans
        "png": _image_parser,
        "jpg": _image_parser,
        "jpeg": _image_parser,
        "webp": _image_parser,
        "bmp": _image_parser,
        "tiff": _image_parser,
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

