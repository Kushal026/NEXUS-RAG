"""
Unit tests for Structured Table Extractor (Phase 8).
"""
import pytest
from app.infrastructure.parsers.table_extractor import TableExtractor


def test_markdown_table_extraction():
    extractor = TableExtractor()
    markdown_text = """
# Experimental Results

Table 1: Benchmark Performance Comparison
| Model | GLUE Score | SQuAD F1 | Latency (ms) |
| :--- | :--- | :--- | :--- |
| BERT-Base | 79.6 | 88.5 | 14.2 |
| RoBERTa | 88.5 | 94.6 | 18.0 |
| Transformer-XL | 91.2 | 95.8 | 22.4 |

Discussion of the benchmark numbers continues here.
"""
    tables = extractor.extract_markdown_tables(markdown_text, default_page=3)

    assert len(tables) == 1
    tbl = tables[0]
    assert tbl.num_rows == 3
    assert tbl.num_cols == 4
    assert tbl.headers == ["Model", "GLUE Score", "SQuAD F1", "Latency (ms)"]
    assert tbl.rows[0] == ["BERT-Base", "79.6", "88.5", "14.2"]
    assert tbl.rows[2][0] == "Transformer-XL"
    assert "Table 1" in tbl.caption
    assert tbl.source_page == 3
    assert "| BERT-Base | 79.6 |" in tbl.markdown_repr


def test_csv_table_extraction():
    extractor = TableExtractor()
    csv_text = """Model,Accuracy,Parameters,Dataset
ResNet-50,76.1%,25.6M,ImageNet
ViT-Base,84.2%,86.0M,ImageNet
ConvNeXt-B,83.8%,88.0M,ImageNet
"""
    table = extractor.extract_from_csv(csv_text, filename="imagenet_benchmarks.csv")

    assert table.num_rows == 3
    assert table.num_cols == 4
    assert table.headers == ["Model", "Accuracy", "Parameters", "Dataset"]
    assert table.rows[1] == ["ViT-Base", "84.2%", "86.0M", "ImageNet"]
    assert "imagenet_benchmarks.csv" in table.caption
    assert table.source_page == 1
