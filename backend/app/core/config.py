"""
Configuration management using pydantic-settings for NEXUS-RAG.
Supports pluggable AI providers, vector stores, and execution modes.
"""
from typing import Optional, Literal
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    PROJECT_NAME: str = "NEXUS-RAG"
    VERSION: str = "0.1.0-phase1"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "data" / "storage"
    DOCUMENTS_DIR: Path = BASE_DIR / "data" / "documents"
    INDEX_DIR: Path = BASE_DIR / "data" / "indices"

    # LLM Settings
    LLM_PROVIDER: Literal["openai", "anthropic", "gemini", "ollama", "local_heuristic"] = "local_heuristic"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048
    
    # API Keys (optional depending on provider)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Embeddings
    EMBEDDING_PROVIDER: Literal["sentence_transformers", "openai", "fastembed", "hash_mock"] = "sentence_transformers"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Retrieval & Reranker
    DEFAULT_TOP_K: int = 10
    DEFAULT_RERANK_TOP_K: int = 5
    HYBRID_DENSE_WEIGHT: float = 0.6
    HYBRID_SPARSE_WEIGHT: float = 0.4
    RRF_K_CONSTANT: int = 60
    
    RERANKER_PROVIDER: Literal["cross_encoder", "none", "heuristic"] = "cross_encoder"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Semantic Chunking defaults
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 120
    MIN_CHUNK_LENGTH: int = 50

    # Knowledge Graph & Neo4j Settings (Phase 5)
    GRAPH_STORAGE_MODE: Literal["auto", "neo4j", "local"] = "auto"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "nexus_graph_password"
    NEO4J_DATABASE: str = "neo4j"
    GRAPH_MAX_HOPS: int = 2
    GRAPH_MIN_CONFIDENCE: float = 0.5
    GRAPH_STORE_PATH: Optional[Path] = None

    # Security, JWT & Multi-Tenancy (Phase 10)
    SECRET_KEY: str = Field(default="nexus_rag_enterprise_secret_key_2026_super_secure", description="JWT Signing Key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Caching
    REDIS_URL: Optional[str] = None


    def init_directories(self) -> None:
        """Ensure all required local directories exist."""
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_directories()

