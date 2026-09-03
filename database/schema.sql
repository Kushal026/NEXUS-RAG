-- NEXUS-RAG Database Schema (PostgreSQL 16 + pgvector)
-- Supports documents, structured chunks, dense vector embeddings, and metadata indexing.

-- Enable pgvector and UUID extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents Table: documents
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(64) PRIMARY KEY,
    lineage_id VARCHAR(64),                                  -- Grouping ID for document family versions
    version VARCHAR(32) DEFAULT '1.0.0',                    -- Document version string (e.g. 1.0.0, 2.0.0, v1)
    filename VARCHAR(512) NOT NULL,
    file_type VARCHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    title VARCHAR(512),
    author VARCHAR(256),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,                                -- Official publication date
    valid_from TIMESTAMPTZ,                                  -- Start of validity epoch
    valid_until TIMESTAMPTZ,                                 -- End of validity epoch (NULL = open-ended)
    is_latest BOOLEAN DEFAULT TRUE,                          -- True if current active version
    superseded_by VARCHAR(64),                               -- ID of newer document version
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    raw_content TEXT,
    chunk_count INT DEFAULT 0
);

-- Table: document_chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    lineage_id VARCHAR(64),
    version VARCHAR(32) DEFAULT '1.0.0',
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    start_char INT NOT NULL,
    end_char INT NOT NULL,
    page_number INT,
    section_title VARCHAR(512),
    valid_from TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    is_latest BOOLEAN DEFAULT TRUE,
    embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Fast Temporal & Lineage Filtering
CREATE INDEX IF NOT EXISTS idx_docs_lineage ON documents(lineage_id, version);
CREATE INDEX IF NOT EXISTS idx_docs_temporal ON documents(valid_from, valid_until, is_latest);
CREATE INDEX IF NOT EXISTS idx_chunks_temporal ON document_chunks(valid_from, valid_until, is_latest);
CREATE INDEX IF NOT EXISTS idx_chunks_lineage ON document_chunks(lineage_id, version);

-- Indices for Fast Querying and Hybrid Retrieval
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_page ON document_chunks(page_number);

-- HNSW Vector Cosine Index for Sub-Millisecond Dense Semantic Retrieval
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Full-Text Lexical Index on Chunks Content
CREATE INDEX IF NOT EXISTS idx_chunks_content_tsv 
ON document_chunks 
USING gin (to_tsvector('english', content));
