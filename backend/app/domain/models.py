"""
Domain Models representing Documents, Chunks, Embeddings, Ingestion,
Hybrid Retrieval, Evidence Citations, Query Reasoning, and Temporal Knowledge.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    version: str = "1.0.0"
    lineage_id: Optional[str] = None
    is_latest: bool = True
    superseded_by: Optional[str] = None
    file_type: str = "unknown"
    file_size: int = 0
    page_count: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content: str
    metadata: DocumentMetadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChunkSpan(BaseModel):
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    chunk_index: int
    content: str
    span: ChunkSpan
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    version: str = "1.0.0"
    lineage_id: Optional[str] = None
    is_latest: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    token_count: Optional[int] = None


class ScoredChunk(BaseModel):
    chunk: DocumentChunk
    dense_score: Optional[float] = None
    dense_rank: Optional[int] = None
    sparse_score: Optional[float] = None
    sparse_rank: Optional[int] = None
    rrf_score: Optional[float] = None
    rerank_score: Optional[float] = None
    final_score: float = 0.0


class TemporalFilter(BaseModel):
    as_of_date: Optional[str] = None       # Point-in-time ISO date / year string (e.g. "2023-12-31" or "2023")
    start_date: Optional[str] = None       # Range start (e.g. "2023-01-01")
    end_date: Optional[str] = None         # Range end (e.g. "2026-12-31")
    version: Optional[str] = None          # Target document version (e.g. "1.0.0")
    latest_only: bool = False              # When true, strictly exclude superseded historical documents


class TemporalConflictType(str, Enum):
    GENUINE_CONTRADICTION = "genuine_contradiction"   # Disagreeing assertions valid at the exact SAME time
    VERSION_CHANGE = "version_change"                 # Newer document version superseded older spec
    TEMPORAL_EVOLUTION = "temporal_evolution"         # Specification or state evolved over chronological epochs
    UNRELATED = "unrelated"                           # Different subjects or non-conflicting


class TemporalConflictResult(BaseModel):
    claim_a: str
    claim_b: str
    timestamp_a: Optional[str] = None
    timestamp_b: Optional[str] = None
    document_a: Optional[str] = None
    document_b: Optional[str] = None
    conflict_type: TemporalConflictType
    explanation: str
    confidence: float = 0.0


class DocumentVersionInfo(BaseModel):
    document_id: str
    lineage_id: str
    version: str
    filename: str
    published_at: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    is_latest: bool = True
    superseded_by: Optional[str] = None
    chunk_count: int = 0


class TemporalClaimDiff(BaseModel):
    attribute: str
    prior_state: str
    prior_date: str
    current_state: str
    current_date: str
    change_type: str = "updated"  # "updated", "deprecated", "added", "superseded"
    explanation: str


class TemporalDiffResult(BaseModel):
    topic: str
    period_from: str
    period_to: str
    diff_summary: str
    detected_changes: List[TemporalClaimDiff] = Field(default_factory=list)
    confidence: float = 0.0


class ExtractedConstraints(BaseModel):
    date_after: Optional[str] = None
    date_before: Optional[str] = None
    as_of_date: Optional[str] = None
    target_documents: List[str] = Field(default_factory=list)
    target_authors: List[str] = Field(default_factory=list)
    target_file_types: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class QueryAnalysis(BaseModel):
    original_query: str
    cleaned_query: str
    intent: str = "factual_lookup"  # factual_lookup, comparative_analysis, temporal_query, conceptual_overview
    keywords: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    constraints: ExtractedConstraints = Field(default_factory=ExtractedConstraints)
    suggested_retrieval_mode: str = "hybrid"


class StageCandidate(BaseModel):
    chunk_id: str
    document_filename: str
    page_number: Optional[int] = None
    score: float
    rank: int
    content_snippet: str


class RetrievalTrace(BaseModel):
    query: str
    query_analysis: Optional[QueryAnalysis] = None
    vector_candidates_count: int = 0
    bm25_candidates_count: int = 0
    fused_candidates_count: int = 0
    reranked_candidates_count: int = 0
    stage_latencies_ms: Dict[str, float] = Field(default_factory=dict)
    vector_top_candidates: List[StageCandidate] = Field(default_factory=list)
    bm25_top_candidates: List[StageCandidate] = Field(default_factory=list)
    fused_top_candidates: List[StageCandidate] = Field(default_factory=list)
    final_ranked_candidates: List[StageCandidate] = Field(default_factory=list)
    total_pipeline_time_ms: float = 0.0


class RetrievalMode(BaseModel):
    use_dense: bool = True
    use_sparse: bool = True
    use_reranker: bool = True
    dense_weight: float = 0.6
    sparse_weight: float = 0.4
    vector_top_k: int = 50
    bm25_top_k: int = 50
    top_k: int = 50
    rerank_top_k: int = 10
    metadata_filter: Optional[Dict[str, Any]] = None
    temporal_filter: Optional[TemporalFilter] = None


class EvidenceCitation(BaseModel):
    citation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chunk_id: str
    document_id: str
    document_filename: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    exact_quote: str
    relevance_score: float
    version: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    is_latest: bool = True


class EvidenceClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str
    supporting_citations: List[EvidenceCitation] = Field(default_factory=list)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    verification_status: str = "supported"  # supported, partially_supported, unverified, contradiction
    temporal_context: Optional[str] = None  # e.g., "Valid as of 2024 (v2.0.0)"


class QueryCategory(str, Enum):
    SIMPLE_FACTUAL = "simple_factual"
    SEMANTIC = "semantic"
    COMPARATIVE = "comparative"
    TEMPORAL = "temporal"
    MULTI_HOP = "multi_hop"
    ANALYTICAL = "analytical"
    RESEARCH = "research"


class PlanStep(BaseModel):
    step_number: int
    sub_query: str
    retrieval_strategy: str = "hybrid"  # "dense", "sparse_bm25", "hybrid", "hybrid_boost_bm25"
    depends_on_step: Optional[int] = None
    expected_output_entity: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"  # "pending", "in_progress", "completed", "failed"


class RetrievalPlan(BaseModel):
    plan_id: str
    original_query: str
    query_category: QueryCategory
    reasoning_summary: str
    steps: List[PlanStep] = Field(default_factory=list)
    estimated_hops: int = 1
    is_multihop: bool = False


class StepEvidence(BaseModel):
    step_number: int
    sub_query: str
    retrieved_chunks: List[ScoredChunk] = Field(default_factory=list)
    extracted_facts: List[str] = Field(default_factory=list)
    discovered_entities: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    was_rewritten: bool = False
    original_sub_query: Optional[str] = None
    execution_time_ms: float = 0.0


class MultiHopReasoningTrace(BaseModel):
    plan: RetrievalPlan
    step_evidences: List[StepEvidence] = Field(default_factory=list)
    total_hops_executed: int = 1
    stop_reason: str = "plan_completed"  # "plan_completed", "max_hops_reached", "confidence_satisfied", "no_new_evidence"
    all_accumulated_chunks: List[ScoredChunk] = Field(default_factory=list)
    total_reasoning_time_ms: float = 0.0


class EvidenceSynthesisResult(BaseModel):
    query: str
    synthesis_markdown: str
    claims: List[EvidenceClaim] = Field(default_factory=list)
    retrieved_chunks: List[ScoredChunk] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_reliability_matrix: Dict[str, float] = Field(default_factory=dict)
    retrieval_trace: Optional[RetrievalTrace] = None
    multihop_trace: Optional[MultiHopReasoningTrace] = None
    temporal_diff: Optional[TemporalDiffResult] = None
    execution_time_ms: float = 0.0
    model_used: str = "local-heuristic-v1"


class EvaluationMetricScores(BaseModel):
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    precision_at_1: float = 0.0
    precision_at_3: float = 0.0
    precision_at_5: float = 0.0
    precision_at_10: float = 0.0
    mrr: float = 0.0
    ndcg_at_5: float = 0.0
    ndcg_at_10: float = 0.0


class MethodBenchmarkResult(BaseModel):
    method_name: str
    description: str
    metrics: EvaluationMetricScores
    average_latency_ms: float = 0.0


class BenchmarkReport(BaseModel):
    benchmark_timestamp: str
    total_test_queries: int
    corpus_documents_count: int
    corpus_chunks_count: int
    results_by_method: Dict[str, MethodBenchmarkResult]
    hybrid_superiority_delta: Dict[str, float]
