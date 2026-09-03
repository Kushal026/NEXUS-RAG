"""
Dense Vector Store implementation with cosine similarity search and persistent serialization.
"""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import numpy as np
from app.domain.models import DocumentChunk, ScoredChunk, TemporalFilter
from app.core.config import settings
from app.core.logging import logger


class DenseVectorStore:
    """In-memory and file-persisted dense vector index with cosine similarity search."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (settings.INDEX_DIR / "vector_store.json")
        self.chunks: Dict[str, DocumentChunk] = {}
        self.vectors: List[np.ndarray] = []
        self.chunk_ids: List[str] = []
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        chunk = DocumentChunk(**item)
                        self.chunks[chunk.id] = chunk
                        if chunk.embedding:
                            self.chunk_ids.append(chunk.id)
                            self.vectors.append(np.array(chunk.embedding, dtype=np.float32))
                logger.info(f"Loaded {len(self.chunks)} chunks into DenseVectorStore from {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to load vector store from {self.storage_path}: {e}")

    def _persist(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = [chunk.model_dump() for chunk in self.chunks.values()]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist vector store: {e}")

    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
            if chunk.embedding is not None:
                # Update existing vector or append
                if chunk.id in self.chunk_ids:
                    idx = self.chunk_ids.index(chunk.id)
                    self.vectors[idx] = np.array(chunk.embedding, dtype=np.float32)
                else:
                    self.chunk_ids.append(chunk.id)
                    self.vectors.append(np.array(chunk.embedding, dtype=np.float32))
        self._persist()
        logger.info(f"Indexed {len(chunks)} chunks in DenseVectorStore (Total: {len(self.chunks)}).")

    def search(
        self,
        query_vector: List[float],
        top_k: int = 50,
        filter_metadata: Optional[Dict[str, Any]] = None,
        temporal_filter: Optional[TemporalFilter] = None
    ) -> List[ScoredChunk]:
        if not self.vectors or not query_vector:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        matrix = np.vstack(self.vectors)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        norm_matrix = matrix / norms

        similarities = np.dot(norm_matrix, q_vec)

        from app.infrastructure.temporal.temporal_filter import TemporalFilterEngine

        # Apply rich metadata filtering
        results: List[ScoredChunk] = []
        sorted_indices = np.argsort(-similarities)

        rank = 1
        for idx in sorted_indices:
            chunk_id = self.chunk_ids[idx]
            chunk = self.chunks[chunk_id]
            score = float(similarities[idx])

            # 1. Temporal Filter Matching
            if temporal_filter:
                if not TemporalFilterEngine.matches_chunk(chunk, temporal_filter):
                    continue

            # 2. Metadata Filter Matching
            if filter_metadata:
                match = True
                for k, v in filter_metadata.items():
                    if not v:
                        continue
                    chunk_meta = chunk.metadata or {}
                    # Target documents filter
                    if k == "filename" or k == "target_documents":
                        target_list = v if isinstance(v, list) else [v]
                        doc_fname = chunk_meta.get("filename", "")
                        if not any(t.lower() in doc_fname.lower() for t in target_list):
                            match = False
                            break
                    elif k == "file_type" or k == "target_file_types":
                        target_types = v if isinstance(v, list) else [v]
                        f_type = chunk_meta.get("file_type", "")
                        if not any(t.lower() == f_type.lower() for t in target_types):
                            match = False
                            break
                    elif k == "author" or k == "target_authors":
                        target_authors = v if isinstance(v, list) else [v]
                        author = chunk_meta.get("author", "")
                        if not any(t.lower() in author.lower() for t in target_authors):
                            match = False
                            break
                    elif chunk_meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            results.append(
                ScoredChunk(
                    chunk=chunk,
                    dense_score=score,
                    dense_rank=rank,
                    final_score=score
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def delete_by_document_id(self, document_id: str) -> None:
        to_delete = [c_id for c_id, c in self.chunks.items() if c.document_id == document_id]
        for c_id in to_delete:
            del self.chunks[c_id]
        
        # Rebuild vector matrix
        new_chunk_ids = []
        new_vectors = []
        for c_id, chunk in self.chunks.items():
            if chunk.embedding:
                new_chunk_ids.append(c_id)
                new_vectors.append(np.array(chunk.embedding, dtype=np.float32))
        self.chunk_ids = new_chunk_ids
        self.vectors = new_vectors
        self._persist()
        logger.info(f"Deleted {len(to_delete)} chunks for document '{document_id}' from DenseVectorStore.")

    def list_all_chunks(self) -> List[DocumentChunk]:
        return list(self.chunks.values())
