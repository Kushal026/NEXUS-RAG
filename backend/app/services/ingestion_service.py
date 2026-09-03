"""
Ingestion Service coordinating multi-format parsing, semantic chunking, embedding, and dual-indexing.
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from app.domain.models import Document, DocumentChunk
from app.infrastructure.parsers.factory import ParserFactory
from app.infrastructure.chunking.semantic_chunker import SemanticChunker
from app.infrastructure.embeddings.embedder import get_embedder
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.core.config import settings
from app.core.logging import logger


class IngestionService:
    """Manages full document lifecycle from ingestion to indexing."""

    def __init__(
        self,
        vector_store: Optional[DenseVectorStore] = None,
        keyword_store: Optional[BM25KeywordStore] = None
    ):
        self.vector_store = vector_store or DenseVectorStore()
        self.keyword_store = keyword_store or BM25KeywordStore()
        self.chunker = SemanticChunker()
        self.embedder = get_embedder()
        self.registry_file = settings.DOCUMENTS_DIR / "document_registry.json"
        self._doc_registry: Dict[str, Dict[str, Any]] = self._load_registry()

        # Re-index existing vector store chunks into BM25 on startup if needed
        all_chunks = self.vector_store.list_all_chunks()
        if all_chunks and not self.keyword_store.chunks:
            self.keyword_store.index_chunks(all_chunks)

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load document registry: {e}")
        return {}

    def _save_registry(self) -> None:
        try:
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self._doc_registry, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save document registry: {e}")

    def ingest_file(
        self,
        file_bytes: bytes,
        filename: str,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingests, parses, chunks, embeds, and indexes a single document."""
        logger.info(f"Starting ingestion for file '{filename}' ({len(file_bytes)} bytes)")
        
        # 1. Parse document
        parser = ParserFactory.get_parser(filename)
        doc = parser.parse(file_bytes, filename, metadata=custom_metadata)

        # 2. Chunk document
        chunks = self.chunker.chunk(doc)
        if not chunks:
            logger.warning(f"No chunks produced for document '{filename}'.")
            return {"document_id": doc.id, "chunks_count": 0, "status": "empty"}

        # 3. Generate embeddings
        texts_to_embed = [c.content for c in chunks]
        embeddings = self.embedder.embed_texts(texts_to_embed)
        
        for idx, chunk in enumerate(chunks):
            chunk.embedding = embeddings[idx]

        # 4. Index in Dense Vector Store & BM25 Keyword Store
        self.vector_store.add_chunks(chunks)
        self.keyword_store.index_chunks(chunks)

        # 5. Save document file copy locally
        save_path = settings.DOCUMENTS_DIR / f"{doc.id}_{filename}"
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # 6. Update document registry
        self._doc_registry[doc.id] = {
            "id": doc.id,
            "filename": filename,
            "file_type": doc.metadata.file_type,
            "file_size": doc.metadata.file_size,
            "page_count": doc.metadata.page_count,
            "chunk_count": len(chunks),
            "created_at": doc.created_at.isoformat(),
            "local_path": str(save_path)
        }
        self._save_registry()

        logger.info(f"Successfully ingested '{filename}': {len(chunks)} chunks indexed.")
        return {
            "document_id": doc.id,
            "filename": filename,
            "file_type": doc.metadata.file_type,
            "page_count": doc.metadata.page_count,
            "chunk_count": len(chunks),
            "status": "indexed"
        }

    def list_documents(self) -> List[Dict[str, Any]]:
        return list(self._doc_registry.values())

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        if document_id in self._doc_registry:
            doc_info = dict(self._doc_registry[document_id])
            local_path = Path(doc_info.get("local_path", ""))
            content_preview = ""
            if local_path.exists():
                try:
                    with open(local_path, "r", encoding="utf-8", errors="replace") as f:
                        content_preview = f.read(50000)
                except Exception:
                    pass
            doc_info["content_preview"] = content_preview
            return doc_info
        return None

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        return [c for c in self.vector_store.list_all_chunks() if c.document_id == document_id]

    def delete_document(self, document_id: str) -> bool:
        if document_id in self._doc_registry:
            doc_info = self._doc_registry[document_id]
            # Remove stored file
            file_path = Path(doc_info.get("local_path", ""))
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not remove file {file_path}: {e}")

            # Remove from indices
            self.vector_store.delete_by_document_id(document_id)
            self.keyword_store.delete_by_document_id(document_id)

            del self._doc_registry[document_id]
            self._save_registry()
            logger.info(f"Document '{document_id}' successfully deleted.")
            return True
        return False
