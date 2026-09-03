"""
Asynchronous Background Job Manager for NEXUS-RAG (Phase 10).
Manages long-running ingestion, indexing, and batch benchmark jobs with real-time status tracking.
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid
import threading
import time
from pydantic import BaseModel, Field
from app.core.logging import logger


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BackgroundJob(BaseModel):
    job_id: str
    job_type: str
    status: JobStatus = JobStatus.QUEUED
    progress_percentage: int = 0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tenant_id: str = "default_tenant"


class BackgroundJobManager:
    """Manages asynchronous job execution and status reporting."""

    def __init__(self):
        self._jobs: Dict[str, BackgroundJob] = {}

    def submit_job(
        self,
        job_type: str,
        task_func: Callable[..., Any],
        args: tuple = (),
        kwargs: dict = None,
        tenant_id: str = "default_tenant"
    ) -> BackgroundJob:
        """Enqueues and launches a background task in a worker thread."""
        kwargs = kwargs or {}
        job_id = f"job-{uuid.uuid4().hex[:8]}"

        job = BackgroundJob(
            job_id=job_id,
            job_type=job_type,
            status=JobStatus.QUEUED,
            progress_percentage=0,
            tenant_id=tenant_id
        )
        self._jobs[job_id] = job

        def _worker():
            job.status = JobStatus.PROCESSING
            job.progress_percentage = 20
            logger.info(f"Background Job {job_id} [{job_type}] started processing.")
            try:
                # Progress simulation/callback if supported
                res = task_func(*args, **kwargs)
                job.progress_percentage = 100
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow().isoformat()
                job.result_data = res if isinstance(res, dict) else {"result": str(res)}
                logger.info(f"Background Job {job_id} [{job_type}] completed successfully.")
            except Exception as e:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow().isoformat()
                job.error_message = str(e)
                logger.error(f"Background Job {job_id} [{job_type}] failed: {e}")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return job

    def get_job(self, job_id: str) -> Optional[BackgroundJob]:
        """Retrieves current job status and metadata."""
        return self._jobs.get(job_id)

    def list_jobs(self, tenant_id: Optional[str] = None) -> List[BackgroundJob]:
        """Lists jobs filtered by tenant."""
        if tenant_id:
            return [j for j in self._jobs.values() if j.tenant_id == tenant_id]
        return list(self._jobs.values())


job_manager = BackgroundJobManager()
