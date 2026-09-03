# NEXUS-RAG Architecture Documentation — Phase 1

**NEXUS-RAG** (*Neural Evidence & eXplainability Unified Search*) is a modular, production-grade evidence intelligence RAG engine designed for deep claim attribution, multi-format ingestion, hybrid retrieval, and explainable AI synthesis.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph UI ["Frontend — Evidence Intelligence Workbench (Next.js 14 + TS + Tailwind)"]
        UI_Dashboard["Dashboard Overview & Telemetry"]
        UI_Vault["Document Vault & Version Lineage Modal"]
        UI_Details["Document Details & Chunk Deep Inspector"]
        UI_Research["Research / Ask (Single-Hop, Multi-Hop, & Temporal Mode)"]
        UI_Timeline["Research Reasoning Timeline (Sequential Multi-Hop Path)"]
        UI_TimeTravel["Temporal Time-Travel Control (Epochs & Latest Only)"]
        UI_Diff["Temporal Evolution & Version Diff Viewer"]
        UI_Waterfall["Retrieval Process Waterfall (5 Stages)"]
        UI_Eval["IR Evaluation & Reasoning Benchmark Suite"]
        UI_Settings["Settings & Model Tuning"]
    end

    subgraph API ["FastAPI REST Layer (/api/v1 & root)"]
        EP_Doc["/documents (Upload, List, Get, Chunks, Lineage, Delete)"]
        EP_Query["/query (Analyze, Search, Synthesize, Stream)"]
        EP_Reason["/reasoning (Plan, MultiHop, Benchmark)"]
        EP_Temporal["/temporal (Query As-Of, Diff, Conflict Check)"]
        EP_Eval["/evaluation (Run IR Benchmark Suite)"]
        EP_Sys["/system (Status, Health)"]
    end

    subgraph Services ["Application Service Layer"]
        IngestSvc["IngestionService"]
        RetSvc["RetrievalService (Multi-Stage with Temporal Filters)"]
        ReasonSvc["QueryReasoningService (Multi-Hop Loop & Guardrails)"]
        TemporalSvc["TemporalService (As-Of Travel & Evolution Diff)"]
        EvSvc["EvidenceService (Streamed & Batch Synthesis)"]
        EvalRunner["RetrievalBenchmarkRunner"]
    end

    subgraph CoreDomain ["Domain Layer (Protocols & Types)"]
        Models["Document | DocumentChunk | ScoredChunk | QueryAnalysis | RetrievalPlan | StepEvidence | TemporalFilter | TemporalDiffResult | TemporalConflictResult"]
        Interfaces["BaseParser | BaseChunker | BaseEmbedder | BaseVectorStore | BaseKeywordStore | BaseReranker | BaseLLMProvider"]
    end

    subgraph Infra ["Infrastructure & Engines"]
        TExtractor["TemporalExtractor\n(As-Of Dates, Ranges, Version Tags)"]
        TFilter["TemporalFilterEngine\n(Point-in-Time & Latest Validity)"]
        TConflict["TemporalConflictResolver\n(Contradiction vs Version vs Evolution)"]
        QClassifier["QueryClassifier\n(7 Structural Complexity Categories)"]
        QDecomposer["QueryDecomposer\n(Atomic Sub-Queries & Dependencies)"]
        QPlanner["RetrievalPlanner\n(DAG Execution Plan Formulation)"]
        QRewriter["QueryRewriter\n(Low Confidence Reformulation)"]
        QAnalyzer["QueryAnalyzer\n(Intent, Entities, Dates, Document Constraints)"]
        Parsers["ParserFactory\n(PyMuPDF, DOCX, BS4 HTML, CSV, TXT)"]
        Chunker["SemanticChunker\n(Structure, Page Bounds, Span Offsets)"]
        Embedder["SentenceTransformerEmbedder\n(all-MiniLM-L6-v2 / OpenAI)"]
        VecStore["DenseVectorStore\n(pgvector HNSW / Temporal Filtering)"]
        BM25Store["BM25KeywordStore\n(Rank-BM25 with Temporal Predicates)"]
        Fusion["HybridFusion\n(Reciprocal Rank Fusion k=60 Top-50)"]
        Reranker["CrossEncoderReranker\n(ms-marco-MiniLM-L-6-v2 Top-10)"]
        LLM["Pluggable LLM Provider\n(OpenAI / Anthropic / LocalHeuristic)"]
    end

    UI --> API
    API --> Services
    Services --> CoreDomain
    Services --> Infra
    TemporalSvc --> TExtractor
    TemporalSvc --> TFilter
    TemporalSvc --> TConflict
    TemporalSvc --> RetSvc
    ReasonSvc --> QClassifier
    ReasonSvc --> QDecomposer
    ReasonSvc --> QPlanner
    ReasonSvc --> QRewriter
    ReasonSvc --> RetSvc
    RetSvc --> TExtractor
    RetSvc --> TFilter
    RetSvc --> QAnalyzer
    RetSvc --> Embedder
    RetSvc --> VecStore
    RetSvc --> BM25Store
    RetSvc --> Fusion
    RetSvc --> Reranker
    EvalRunner --> RetSvc
```

---

## 2. Ingestion Pipeline

1. **Multi-Format Extraction**:
   - **PDF**: PyMuPDF (`fitz`) parses text, extracts metadata (author, title), and inserts structural `<!-- PAGE_X -->` boundary markers.
   - **DOCX**: `python-docx` extracts paragraphs, header styles (`## Heading`), and structured markdown tables.
   - **HTML**: `BeautifulSoup4` strips scripts/styles and extracts structured semantic text.
   - **CSV**: Converts raw tabular datasets into markdown grid tables.
   - **Markdown/TXT**: Preserves header hierarchies and raw formatting.

2. **Structure-Aware Semantic Chunking**:
   - Splits on paragraph and header boundaries while maintaining sentence coherence.
   - Tracks exact token counts, character spans (`start_char`, `end_char`), page numbers, and section headers.
   - Automatically flushes and aligns chunks at page transitions for clear citation attribution.

3. **Dual-Index Registration**:
   - Dense vector embeddings generated via `SentenceTransformerEmbedder`.
   - Lexical tokenization indexed via `BM25KeywordStore`.

---

## 3. Hybrid Retrieval & Reranking Mathematics

### Reciprocal Rank Fusion (RRF)
To combine dense semantic vectors and sparse lexical keyword rankings without requiring calibrated raw score normalization:

$$RRF(d) = \sum_{m \in \{dense, sparse\}} \frac{w_m}{k + \text{rank}_m(d)}$$

Where:
- $k = 60$ (smoothing constant)
- $w_{dense} = 0.6$, $w_{sparse} = 0.4$ (configurable per query)

### Cross-Encoder Neural Reranking
Top-$K$ candidates from RRF fusion are passed to a neural Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) which evaluates query-document token interactions simultaneously:

$$\text{Score}_{rerank}(q, d) = \sigma\left(\text{CrossEncoder}(q, d)\right)$$

---

## 4. Evidence Synthesis & Claim-Level Citations

- **Claim Extraction**: The synthesis engine extracts discrete factual claims from evidence passages.
- **Attribution & Spans**: Every claim is mapped to supporting citations with exact passage quotes, source document filename, page number, and chunk index.
- **Verification Status**: Each claim receives a verification tag (`supported`, `partially_supported`, `unverified`).
- **Source Reliability Matrix**: Computes weighted contribution of each source document based on retrieval confidence.
