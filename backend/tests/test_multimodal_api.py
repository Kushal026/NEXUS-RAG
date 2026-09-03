"""
Integration tests for FastAPI Multimodal Evidence Endpoints (Phase 8).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_multimodal_query_api():
    response = client.post(
        "/api/v1/multimodal/query",
        json={"query": "Transformer architecture benchmarks and tables", "requested_modality": "all", "top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "evidence_items" in data
    assert "modality_counts" in data
    assert "synthesis_markdown" in data
    assert "overall_confidence" in data


def test_multimodal_parse_text_api():
    sample_md = """
# System Benchmark

Table 1: Latency Table
| Batch | Time |
| 1 | 10ms |

Figure 1: Latency Plot
Plots latency over batch size.

```python
def benchmark():
    pass
```
"""
    response = client.post(
        "/api/v1/multimodal/parse-text",
        json={"text": sample_md, "filename": "benchmark.md"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "benchmark.md"
    assert len(data["tables"]) == 1
    assert len(data["figures"]) == 1
    assert len(data["code_blocks"]) == 1
