"""
API Endpoints for Phase 8 — Multimodal Evidence Engine.
Provides cross-modality retrieval (Text, Tables, Figures, Images, Code), structural parsing, and provenance tracking.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from app.domain.models import (
    MultimodalRetrievalResult,
    MultimodalDocumentRepresentation,
    Document,
    DocumentMetadata
)
from app.services.multimodal_service import MultimodalService
from app.services.ingestion_service import IngestionService
from app.core.logging import logger

router = APIRouter(prefix="/multimodal", tags=["Multimodal Evidence Engine"])

multimodal_service = MultimodalService()
ingestion_service = IngestionService()


class MultimodalQueryRequest(BaseModel):
    query: str
    requested_modality: Optional[str] = "all"  # all, table, figure, code, image, text
    top_k: int = 8


class ParseTextRequest(BaseModel):
    text: str
    filename: Optional[str] = "document.md"


@router.post("/query", response_model=MultimodalRetrievalResult)
def query_multimodal_evidence(request: MultimodalQueryRequest):
    """
    Executes cross-modality retrieval across Text, Tables, Figures/Charts, Images/OCR, and Code.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    return multimodal_service.retrieve_multimodal_evidence(
        query=request.query,
        requested_modality=request.requested_modality,
        top_k=request.top_k
    )


@router.post("/parse-text", response_model=MultimodalDocumentRepresentation)
def parse_multimodal_text(request: ParseTextRequest):
    """
    Parses raw text into full multimodal document representation:
    Document -> Text | Tables | Figures | Images | Code | Metadata | References
    """
    doc = Document(
        filename=request.filename or "sample.md",
        content=request.text,
        metadata=DocumentMetadata(
            title=request.filename or "Sample Multimodal Document",
            file_type="markdown",
            file_size=len(request.text.encode("utf-8")),
            page_count=1
        )
    )
    return multimodal_service.build_document_representation(doc)


@router.get("/document/{document_id}/structure", response_model=MultimodalDocumentRepresentation)
def get_document_structure(document_id: str):
    """
    Retrieves the complete multimodal document hierarchy for an ingested document.
    """
    doc = ingestion_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found.")

    chunks = ingestion_service.get_document_chunks(document_id)
    return multimodal_service.build_document_representation(doc, chunks)
