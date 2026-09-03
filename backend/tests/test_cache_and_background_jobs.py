"""
Unit tests for Cache Engine & Async Background Jobs (Phase 10).
"""
import pytest
import time
from app.infrastructure.cache.redis_cache import CacheManager
from app.infrastructure.jobs.background_job_manager import BackgroundJobManager, JobStatus


def test_cache_set_get_and_ttl():
    cache = CacheManager(redis_url=None)  # Use in-memory fallback
    cache.clear()

    key = {"query": "deepfake detection", "top_k": 5}
    value = {"results": ["chunk1", "chunk2"]}

    # Miss
    assert cache.get("retrieval", key) is None
    assert cache.misses == 1

    # Set and Hit
    cache.set("retrieval", key, value, ttl_seconds=10)
    cached_val = cache.get("retrieval", key)
    assert cached_val == value
    assert cache.hits == 1

    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["cached_items_count"] >= 1


def test_background_job_lifecycle():
    mgr = BackgroundJobManager()

    def sample_heavy_indexing(doc_name: str):
        time.sleep(0.05)
        return {"processed_chunks": 42, "doc": doc_name}

    job = mgr.submit_job(
        job_type="document_indexing",
        task_func=sample_heavy_indexing,
        args=("quantum_computing.pdf",),
        tenant_id="tenant_quantum"
    )

    assert job.job_id.startswith("job-")
    assert job.job_type == "document_indexing"
    assert job.tenant_id == "tenant_quantum"

    # Wait for completion
    time.sleep(0.15)
    updated_job = mgr.get_job(job.job_id)
    assert updated_job.status == JobStatus.COMPLETED
    assert updated_job.progress_percentage == 100
    assert updated_job.result_data["processed_chunks"] == 42
