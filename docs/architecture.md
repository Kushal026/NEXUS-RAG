# NEXUS-RAG System Architecture Specification

## 1. Architectural Philosophy

NEXUS-RAG is engineered as a multi-tier, decoupled, fault-tolerant research intelligence platform designed around the following core principles:
1. **Explainability First**: Every retrieved claim, synthesized finding, and graph connection retains full cryptographic and spatial provenance (`document_id`, `chunk_id`, `page_number`, `bounding_box/span`).
2. **Untrusted Data Boundary**: Documents are treated as untrusted data inputs protected by strict `<untrusted_document_context>` XML boundaries to prevent prompt injection and instruction hijack.
3. **Iterative Self-Correction**: Static single-pass RAG is replaced with an autonomous evaluation-and-recovery loop that detects evidence gaps and contradiction points.
4. **Hybrid Retrieval Synthesis**: Sparse lexical indexing (BM25) and dense neural embeddings (MiniLM) are fused via Reciprocal Rank Fusion ($k=60$) and reranked using a deep cross-encoder.

---

## 2. Component Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                      NEXUS Web Application (Next.js 14)                            |
|  [ Dashboard | Documents | Research | Knowledge Graph | Evidence | Multimodal | Agent | Evaluation ]  |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                             REST / JSON
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                    FastAPI Application Gateway                                    |
|   - Rate Limiter (Token Bucket)        - Prompt Injection Filter       - JWT Auth & RBAC Guard    |
|   - SSRF Outbound Validator            - Multi-Tenancy Scoper          - Prometheus Telemetry     |
+---------------------------------------------------------------------------------------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                        |                                        |
         v                                        v                                        v
+------------------------+              +------------------------+              +------------------------+
|  NEXUS Research Agent  |              |   Evidence & NLI Engine|              |  Knowledge Graph RAG   |
| - Research Planner     |              | - Pairwise NLI Checker |              | - Neo4j / In-Memory    |
| - Gap Detector         |              | - Contradiction Parser |              | - Entity Resolution    |
| - 9-Section Synthesizer|              | - Source Reliability   |              | - Subgraph Traversal   |
+------------------------+              +------------------------+              +------------------------+
         |                                        |                                        |
         +----------------------------------------+----------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 Self-Correcting Retrieval Core                                     |
|  - Quality Evaluator (Relevance, Coverage, Redundancy, Temporal Suitability)                       |
|  - Targeted Query Rewriter (Missing Parameters / Disambiguation)                                  |
|  - Evidence Accumulator (Multi-Iteration Retention)                                               |
|  - Answer Verifier (Zero-Hallucination Claim Entailment)                                          |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 Hybrid Retrieval & Multimodal Index                               |
|  - Dense Vector Store (Cosine Similarity, MiniLM-L6-v2)                                           |
|  - Sparse BM25 Store (Term Frequency, Inverted Index)                                             |
|  - Cross-Encoder Reranker (ms-marco-MiniLM-L-6-v2)                                                |
|  - Multimodal Parsers (Tables, Chart Figures, Images/OCR, Source Code)                            |
|  - Redis Cache & Background Job Queue                                                             |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Data Flow Specification

### 3.1 Document Ingestion Flow
1. **Upload**: User uploads file (`PDF`, `CSV`, `DOCX`, `MD`, `HTML`, `PNG/JPG`, `Code`).
2. **Validation**: Enforces 50MB file size limit, magic byte validation, and script stripping.
3. **Multimodal Extraction**:
   - `TableExtractor`: Extracts structured rows, headers, and column relationships.
   - `ChartFigureExtractor`: Extracts chart titles, X/Y axis labels, visible values, and captions.
   - `CodeParser`: Tokenizes functions, classes, and code syntax across 15+ languages.
   - `ImageOCRParser`: Extracts OCR text with spatial bounding coordinates.
4. **Chunking**: Chunked with overlap, preserving page and section provenance.
5. **Graph Construction**: Extracts named entities (`Person`, `Model`, `Dataset`, `Technology`), links relationships, resolves duplicates via Jaro-Winkler distance, and indexes nodes in Neo4j.
6. **Dual Indexing**: Concurrently indexed in the Sparse BM25 store and Dense Vector store.

### 3.2 Autonomous Research Query Flow
1. **Plan Formulation**: Goal is decomposed into 4 analytical sub-questions + domain entities.
2. **Graph Traversal**: Subgraph entity neighborhoods are retrieved for multi-hop context.
3. **Iterative Retrieval**: Hybrid dense-sparse search retrieves candidate passages per sub-question.
4. **Cross-Encoder Reranking**: Scores and filters candidate passages by deep semantic relevance.
5. **NLI Contradiction Analysis**: Top passages are evaluated pairwise to detect discrepancies and conflicting conditions.
6. **Gap Detection**: Evaluates if all sub-questions are answered; if gaps are found, generates targeted follow-up queries.
7. **Synthesis & Verification**: Compiles a 9-section report with strict citation provenance and executes zero-hallucination factual claim verification.
