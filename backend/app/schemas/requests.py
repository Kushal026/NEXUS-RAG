"""
API Request and Response schemas for NEXUS-RAG.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.domain.models import ScoredChunk, EvidenceSynthesisResult, DocumentChunk


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query or research question")
    use_dense: bool = Field(default=True, description="Enable dense vector search")
    use_sparse: bool = Field(default=True, description="Enable sparse BM25 keyword search")
    use_reranker: bool = Field(default=True, description="Enable cross-encoder neural reranking")
    dense_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    sparse_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    top_k: int = Field(default=10, ge=1, le=50)
    rerank_top_k: int = Field(default=5, ge=1, le=20)
    metadata_filter: Optional[Dict[str, Any]] = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    page_count: Optional[int] = None
    chunk_count: int
    status: str


class DocumentInfoResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    page_count: Optional[int] = None
    chunk_count: int
    created_at: str
    local_path: Optional[str] = None


class SystemStatusResponse(BaseModel):
    project_name: str
    version: str
    environment: str
    llm_provider: str
    embedding_provider: str
    reranker_provider: str
    total_documents: int
    total_chunks: int
    status: str = "operational"
