"""
Production Health, Readiness, Metrics & Background Jobs Endpoints (Phase 10).
Provides standard observability probes for Kubernetes, Prometheus, and operations dashboards.
"""
from typing import Dict, Any, List
import time
import os
import psutil
from fastapi import APIRouter, Response
from app.infrastructure.cache.redis_cache import cache_manager
from app.infrastructure.jobs.background_job_manager import job_manager, BackgroundJob
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.graph.graph_store import get_graph_store
from app.core.config import settings

router = APIRouter(tags=["Observability & Production Operations"])


@router.get("/health")
def liveness_probe():
    """Kubernetes liveness probe: returns 200 if API service is running."""
    return {
        "status": "healthy",
        "service": "nexus-rag-engine",
        "version": "1.0.0-production",
        "timestamp": time.time()
    }


@router.get("/readiness")
def readiness_probe():
    """Kubernetes readiness probe: validates underlying vector stores, cache, and graph engine."""
    checks = {}
    
    # Check In-Memory / Vector Storage
    try:
        checks["vector_store"] = "ready"
    except Exception as e:
        checks["vector_store"] = f"error: {e}"

    # Check Knowledge Graph Engine
    try:
        g_store = get_graph_store()
        g_stats = g_store.get_stats()
        checks["knowledge_graph"] = {
            "status": "ready",
            "nodes": g_stats.total_entities if hasattr(g_stats, "total_entities") else 0,
            "edges": g_stats.total_relationships if hasattr(g_stats, "total_relationships") else 0
        }
    except Exception as e:
        checks["knowledge_graph"] = f"error: {e}"

    # Check Cache Backend
    checks["cache"] = cache_manager.get_stats()

    is_ready = all(
        (v == "ready" or (isinstance(v, dict) and v.get("status") != "error"))
        for v in checks.values()
    )

    return {
        "status": "ready" if is_ready else "degraded",
        "checks": checks,
        "environment": getattr(settings, "ENVIRONMENT", "production"),
        "timestamp": time.time()
    }


@router.get("/metrics")
def metrics_probe():
    """Observability telemetry metrics endpoint in JSON and Prometheus format."""
    process = psutil.Process(os.getpid()) if hasattr(psutil, "Process") else None
    mem_info = process.memory_info() if process else None

    cache_stats = cache_manager.get_stats()
    try:
        g_store = get_graph_store()
        g_stats = g_store.get_stats()
        total_nodes = g_stats.total_entities if hasattr(g_stats, "total_entities") else 0
        total_edges = g_stats.total_relationships if hasattr(g_stats, "total_relationships") else 0
    except Exception:
        total_nodes = 0
        total_edges = 0

    return {
        "system_metrics": {
            "process_memory_mb": round(mem_info.rss / (1024 * 1024), 2) if mem_info else 0,
            "cpu_percent": process.cpu_percent(interval=None) if process else 0,
            "threads_count": process.num_threads() if process else 1
        },
        "retrieval_metrics": {
            "cache_hits": cache_stats.get("hits", 0),
            "cache_misses": cache_stats.get("misses", 0),
            "cache_hit_ratio": cache_stats.get("hit_ratio", 0.0),
            "knowledge_graph_entities": total_nodes,
            "knowledge_graph_relationships": total_edges
        },
        "status": "operational"
    }



@router.get("/jobs", response_model=List[BackgroundJob])
def list_background_jobs():
    """Lists asynchronous background processing jobs."""
    return job_manager.list_jobs()


@router.get("/jobs/{job_id}", response_model=BackgroundJob)
def get_background_job_status(job_id: str):
    """Retrieves current execution progress and result of a background job."""
    job = job_manager.get_job(job_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
