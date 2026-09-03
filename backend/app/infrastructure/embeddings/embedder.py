"""
Configurable Embedder supporting SentenceTransformers, OpenAI, and fallback embedding engines.
"""
from typing import List, Optional
import numpy as np
import hashlib
from app.domain.interfaces import BaseEmbedder
from app.core.config import settings
from app.core.logging import logger


class SentenceTransformerEmbedder:
    """Generates dense embeddings using sentence-transformers models."""

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            model = self._get_model()
            embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error in SentenceTransformer embedding: {e}, falling back to deterministic embedder")
            fallback = DeterministicHashEmbedder(dim=settings.EMBEDDING_DIMENSION)
            return fallback.embed_texts(texts)

    def embed_query(self, query: str) -> List[float]:
        res = self.embed_texts([query])
        return res[0] if res else [0.0] * settings.EMBEDDING_DIMENSION


class OpenAIEmbedder:
    """Generates embeddings using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if not self.api_key:
            logger.warning("No OpenAI API key found, falling back to SentenceTransformers")
            return SentenceTransformerEmbedder().embed_texts(texts)
            
        import httpx
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"input": texts, "model": self.model}
        
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    def embed_query(self, query: str) -> List[float]:
        res = self.embed_texts([query])
        return res[0] if res else []


class DeterministicHashEmbedder:
    """Fast deterministic pseudo-semantic embedder for tests and low-resource environments."""

    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dim, dtype=np.float32)
            words = text.lower().split()
            for word in words:
                h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        res = self.embed_texts([query])
        return res[0]


def get_embedder() -> BaseEmbedder:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "openai":
        return OpenAIEmbedder()
    elif provider == "hash_mock":
        return DeterministicHashEmbedder(dim=settings.EMBEDDING_DIMENSION)
    else:
        return SentenceTransformerEmbedder(model_name=settings.EMBEDDING_MODEL)
