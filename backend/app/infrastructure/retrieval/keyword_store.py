"""
Sparse lexical retrieval engine using BM25 Okapi.
"""
from typing import List, Dict, Any, Optional
import re
from rank_bm25 import BM25Okapi
from app.domain.models import DocumentChunk, ScoredChunk, TemporalFilter
from app.core.logging import logger


class BM25KeywordStore:
    """In-memory BM25 Okapi search index."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.corpus_tokens: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, clean alphanumeric tokens
        clean_text = re.sub(r"[^\w\s]", " ", text.lower())
        return [t for t in clean_text.split() if len(t) > 1]

    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        # Avoid duplicate chunk IDs
        existing_ids = {c.id for c in self.chunks}
        new_chunks = [c for c in chunks if c.id not in existing_ids]
        
        self.chunks.extend(new_chunks)
        self.corpus_tokens = [self._tokenize(c.content) for c in self.chunks]
        
        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)
            logger.info(f"Indexed {len(self.chunks)} total chunks in BM25KeywordStore.")
        else:
            self.bm25 = None

    def search(
        self,
        query: str,
        top_k: int = 50,
        filter_metadata: Optional[Dict[str, Any]] = None,
        temporal_filter: Optional[TemporalFilter] = None
    ) -> List[ScoredChunk]:
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        doc_scores = self.bm25.get_scores(query_tokens)
        
        # Normalize scores to 0..1 range for fusion compatibility
        max_score = max(doc_scores) if len(doc_scores) > 0 and max(doc_scores) > 0 else 1.0
        
        sorted_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)

        from app.infrastructure.temporal.temporal_filter import TemporalFilterEngine

        results: List[ScoredChunk] = []
        rank = 1
        for idx in sorted_indices:
            score = float(doc_scores[idx])
            if score <= 0:
                continue

            chunk = self.chunks[idx]

            # 1. Temporal Filter Matching
            if temporal_filter:
                if not TemporalFilterEngine.matches_chunk(chunk, temporal_filter):
                    continue

            # 2. Metadata Filter Matching
            if filter_metadata:
                match = True
                chunk_meta = chunk.metadata or {}
                for k, v in filter_metadata.items():
                    if not v:
                        continue
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

            norm_score = score / max_score
            results.append(
                ScoredChunk(
                    chunk=chunk,
                    sparse_score=norm_score,
                    sparse_rank=rank,
                    final_score=norm_score
                )
            )
            rank += 1
            if len(results) >= top_k:
                break

        return results

    def delete_by_document_id(self, document_id: str) -> None:
        self.chunks = [c for c in self.chunks if c.document_id != document_id]
        self.corpus_tokens = [self._tokenize(c.content) for c in self.chunks]
        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)
        else:
            self.bm25 = None
        logger.info(f"Deleted chunks for document '{document_id}' from BM25KeywordStore.")
