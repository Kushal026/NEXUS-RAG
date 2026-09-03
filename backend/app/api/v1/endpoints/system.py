"""
System status, health, and configuration endpoints.
"""
from fastapi import APIRouter, Depends
from app.schemas.requests import SystemStatusResponse
from app.core.config import settings
from app.services.ingestion_service import IngestionService
from app.api.v1.endpoints.documents import get_ingestion_service

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(service: IngestionService = Depends(get_ingestion_service)):
    docs = service.list_documents()
    chunks = service.vector_store.list_all_chunks()
    return SystemStatusResponse(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        llm_provider=settings.LLM_PROVIDER,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        reranker_provider=settings.RERANKER_PROVIDER,
        total_documents=len(docs),
        total_chunks=len(chunks),
        status="operational"
    )


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "NEXUS-RAG", "version": settings.VERSION}
