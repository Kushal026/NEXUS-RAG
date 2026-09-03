"""
Documents API endpoints: Multi-format upload, listing, chunk inspection, and deletion.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.services.ingestion_service import IngestionService
from app.schemas.requests import DocumentUploadResponse, DocumentInfoResponse
from app.domain.models import DocumentChunk
import json

router = APIRouter(prefix="/documents", tags=["Documents"])

# Singleton injection
_ingestion_service: Optional[IngestionService] = None

def get_ingestion_service() -> IngestionService:
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    custom_metadata_json: Optional[str] = Form(None),
    service: IngestionService = Depends(get_ingestion_service)
):
    """Upload and ingest a document (PDF, DOCX, TXT, MD, HTML, CSV)."""
    try:
        content = await file.read()
        custom_metadata = {}
        if custom_metadata_json:
            try:
                custom_metadata = json.loads(custom_metadata_json)
            except Exception:
                pass

        result = service.ingest_file(
            file_bytes=content,
            filename=file.filename or "unknown_file",
            custom_metadata=custom_metadata
        )
        return DocumentUploadResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")


@router.get("", response_model=List[DocumentInfoResponse])
async def list_documents(service: IngestionService = Depends(get_ingestion_service)):
    """List all indexed documents in the vault."""
    docs = service.list_documents()
    return [DocumentInfoResponse(**d) for d in docs]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    service: IngestionService = Depends(get_ingestion_service)
):
    """Retrieve metadata and information for a specific document."""
    doc = service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{document_id}/chunks", response_model=List[DocumentChunk])
async def get_document_chunks(
    document_id: str,
    service: IngestionService = Depends(get_ingestion_service)
):
    """Inspect all parsed and extracted chunks for a specific document."""
    chunks = service.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for the given document ID")
    return chunks


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    service: IngestionService = Depends(get_ingestion_service)
):
    """Delete a document and all its indexed chunks from both Dense and Sparse indices."""
    success = service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}
