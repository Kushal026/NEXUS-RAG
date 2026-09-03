"""
Unit tests for multi-format document parsers.
"""
import pytest
from app.infrastructure.parsers.factory import ParserFactory
from app.infrastructure.parsers.text_parser import PlainTextParser, HTMLParser, CSVParser


def test_plaintext_parser():
    content = b"# Document Title\n\nThis is a sample markdown document with facts."
    parser = PlainTextParser()
    doc = parser.parse(content, "test.md")
    assert doc.filename == "test.md"
    assert "sample markdown document" in doc.content
    assert doc.metadata.file_type in ["md", "markdown"]


def test_html_parser():
    html_content = b"<html><head><title>Test Article</title></head><body><h1>Title</h1><p>Neural search is powerful.</p></body></html>"
    parser = HTMLParser()
    doc = parser.parse(html_content, "article.html")
    assert doc.metadata.title == "Test Article"
    assert "Neural search is powerful." in doc.content


def test_csv_parser():
    csv_content = b"Entity,Score,Category\nAlpha,0.95,AI\nBeta,0.88,Cloud"
    parser = CSVParser()
    doc = parser.parse(csv_content, "data.csv")
    assert "Entity | Score | Category" in doc.content
    assert "Alpha | 0.95 | AI" in doc.content


def test_parser_factory():
    p_pdf = ParserFactory.get_parser("report.pdf")
    p_docx = ParserFactory.get_parser("summary.docx")
    p_txt = ParserFactory.get_parser("notes.txt")
    p_html = ParserFactory.get_parser("page.html")
    
    assert p_pdf is not None
    assert p_docx is not None
    assert p_txt is not None
    assert p_html is not None
