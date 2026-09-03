"""
Abstract interfaces and protocols for NEXUS-RAG components.
Adheres to Clean Architecture and Dependency Inversion Principle.
"""
from typing import Protocol, List, Dict, Any, Optional, BinaryIO
from app.domain.models import (
    Document,
    DocumentChunk,
    ScoredChunk,
    RetrievalMode,
    EvidenceSynthesisResult
)


class BaseParser(Protocol):
    """Protocol for document file parsers."""
    def parse(self, file_content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        ...


class BaseChunker(Protocol):
    """Protocol for document chunking algorithms."""
    def chunk(self, document: Document) -> List[DocumentChunk]:
        ...


class BaseEmbedder(Protocol):
    """Protocol for embedding generation."""
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        ...

    def embed_query(self, query: str) -> List[float]:
        ...


class BaseVectorStore(Protocol):
    """Protocol for dense vector storage & retrieval."""
    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        ...

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ScoredChunk]:
        ...

    def delete_by_document_id(self, document_id: str) -> None:
        ...

    def list_all_chunks(self) -> List[DocumentChunk]:
        ...


class BaseKeywordStore(Protocol):
    """Protocol for sparse/lexical keyword retrieval (e.g., BM25)."""
    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        ...

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[ScoredChunk]:
        ...

    def delete_by_document_id(self, document_id: str) -> None:
        ...


class BaseReranker(Protocol):
    """Protocol for cross-encoder reranking."""
    def rerank(self, query: str, scored_chunks: List[ScoredChunk], top_k: int = 5) -> List[ScoredChunk]:
        ...


class BaseLLMProvider(Protocol):
    """Protocol for LLM evidence synthesis."""
    def generate_synthesis(
        self,
        query: str,
        evidence_chunks: List[ScoredChunk]
    ) -> EvidenceSynthesisResult:
        ...


class BaseGraphStore(Protocol):
    """Protocol for Knowledge Graph storage, traversal, and querying (Neo4j / Local)."""
    def upsert_entity(self, entity: Any) -> Any:
        ...

    def upsert_relationship(self, edge: Any) -> Any:
        ...

    def get_entity_by_id(self, entity_id: str) -> Optional[Any]:
        ...

    def find_entity_by_name(self, name: str) -> Optional[Any]:
        ...

    def search_entities(self, query: str, entity_type: Optional[str] = None, limit: int = 50) -> List[Any]:
        ...

    def get_neighborhood(self, entity_id: str, depth: int = 1) -> Any:
        ...

    def find_paths(self, source_name: str, target_name: str, max_depth: int = 3) -> List[Any]:
        ...

    def get_stats(self) -> Any:
        ...

    def delete_by_document_id(self, document_id: str) -> int:
        ...

    def clear(self) -> None:
        ...

