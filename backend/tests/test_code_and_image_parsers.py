"""
Unit tests for Code Parser and Image OCR Parser (Phase 8).
"""
import pytest
from app.infrastructure.parsers.code_parser import CodeParser
from app.infrastructure.parsers.image_ocr_parser import ImageOCRParser
from app.infrastructure.parsers.factory import ParserFactory


def test_code_parser_and_markdown_blocks():
    parser = CodeParser()
    py_code = b"def scaled_dot_product(q, k, v):\n    return torch.matmul(q, k.transpose(-2, -1))\n"
    doc = parser.parse(py_code, filename="attention.py")

    assert doc.metadata.file_type == "code_python"
    assert "scaled_dot_product" in doc.content

    md_text = """
Here is the implementation:
```python
def forward(x):
    return self.layer_norm(x)
```
And TypeScript version:
```typescript
export function computeLoss(y: number[]): number {
    return 0.05;
}
```
"""
    blocks = parser.extract_code_blocks_from_markdown(md_text, default_page=2)
    assert len(blocks) == 2
    assert blocks[0].language == "python"
    assert "forward" in blocks[0].code_content
    assert blocks[1].language == "typescript"
    assert "computeLoss" in blocks[1].code_content


def test_image_ocr_parser():
    parser = ImageOCRParser()
    dummy_img_content = b"\x89PNG\r\n\x1a\nArchitectural Diagram: Encoder-Decoder Network"
    doc = parser.parse(dummy_img_content, filename="diagram.png")

    assert doc.metadata.file_type == "image_png"
    assert doc.metadata.custom_attributes.get("image_type") == "diagram"
    assert "IMAGE: diagram.png" in doc.content



def test_parser_factory_multimodal_support():
    assert "png" in ParserFactory.supported_extensions()
    assert "py" in ParserFactory.supported_extensions()
    assert "csv" in ParserFactory.supported_extensions()
    assert "docx" in ParserFactory.supported_extensions()
    assert "pdf" in ParserFactory.supported_extensions()
