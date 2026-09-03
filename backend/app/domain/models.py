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


# ============================================================================
# PHASE 5 — KNOWLEDGE GRAPH INTELLIGENCE MODELS
# ============================================================================

class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    COMPANY = "company"
    TECHNOLOGY = "technology"
    MODEL = "model"
    PAPER = "paper"
    DATASET = "dataset"
    CONCEPT = "concept"
    EVENT = "event"
    PRODUCT = "product"
    LOCATION = "location"
    DATE = "date"


class RelationshipType(str, Enum):
    AUTHORED_BY = "AUTHORED_BY"
    CREATED_BY = "CREATED_BY"
    USES = "USES"
    DEPENDS_ON = "DEPENDS_ON"
    INTRODUCED = "INTRODUCED"
    EVALUATED_ON = "EVALUATED_ON"
    COMPETES_WITH = "COMPETES_WITH"
    RELATED_TO = "RELATED_TO"
    PRECEDED_BY = "PRECEDED_BY"
    SUCCEEDED_BY = "SUCCEEDED_BY"
    AFFILIATED_WITH = "AFFILIATED_WITH"
    PART_OF = "PART_OF"
    TRAINED_ON = "TRAINED_ON"


class GraphProvenance(BaseModel):
    document_id: str
    document_filename: str
    chunk_id: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    exact_snippet: str
    confidence: float = 1.0
    extracted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class EntityNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    canonical_name: str
    entity_type: EntityType = EntityType.CONCEPT
    aliases: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    mention_count: int = 1
    provenance_list: List[GraphProvenance] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class RelationshipEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    description: Optional[str] = None
    weight: float = 1.0
    provenance_list: List[GraphProvenance] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class KnowledgeGraphSubgraph(BaseModel):
    nodes: List[EntityNode] = Field(default_factory=list)
    edges: List[RelationshipEdge] = Field(default_factory=list)
    query_entity_id: Optional[str] = None
    depth: int = 1
    total_nodes: int = 0
    total_edges: int = 0


class GraphPath(BaseModel):
    nodes: List[EntityNode] = Field(default_factory=list)
    edges: List[RelationshipEdge] = Field(default_factory=list)
    path_description: str
    hops: int = 1


class GraphStats(BaseModel):
    total_entities: int = 0
    total_relationships: int = 0
    entity_types_count: Dict[str, int] = Field(default_factory=dict)
    relationship_types_count: Dict[str, int] = Field(default_factory=dict)
    storage_engine: str = "local_memory"
    connected: bool = True


class HybridGraphRAGResult(BaseModel):
    query: str
    synthesis_markdown: str
    claims: List[EvidenceClaim] = Field(default_factory=list)
    retrieved_chunks: List[ScoredChunk] = Field(default_factory=list)
    graph_entities: List[EntityNode] = Field(default_factory=list)
    graph_relationships: List[RelationshipEdge] = Field(default_factory=list)
    graph_paths: List[GraphPath] = Field(default_factory=list)
    subgraph: Optional[KnowledgeGraphSubgraph] = None
    overall_confidence: float = 0.0
    execution_time_ms: float = 0.0
    model_used: str = "hybrid_graph_rag_v1"


# ============================================================================
# PHASE 6 — EVIDENCE INTELLIGENCE ENGINE MODELS
# ============================================================================

class NLIClassificationType(str, Enum):
    ENTAILMENT = "entailment"
    CONTRADICTION = "contradiction"
    PARTIAL_CONTRADICTION = "partial_contradiction"
    DIFFERENT_CONDITIONS = "different_conditions"
    TEMPORAL_DIFFERENCE = "temporal_difference"
    NEUTRAL = "neutral"


class NLIResult(BaseModel):
    premise: str
    hypothesis: str
    verdict: NLIClassificationType = NLIClassificationType.NEUTRAL
    confidence: float = 0.0
    explanation: str
    condition_a: Optional[str] = None
    condition_b: Optional[str] = None
    metric_diff: Optional[str] = None


class SourceReliabilityScore(BaseModel):
    document_filename: str
    overall_score: float = 0.5
    source_type_score: float = 0.5
    authority_score: float = 0.5
    recency_score: float = 0.5
    corroboration_score: float = 0.5
    citation_quality_score: float = 0.5
    document_type: str = "unknown"
    explanation: str


class GroupedClaimEvidence(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str
    supporting_citations: List[EvidenceCitation] = Field(default_factory=list)
    contradicting_citations: List[EvidenceCitation] = Field(default_factory=list)
    conflict_explanation: Optional[str] = None
    has_conflict: bool = False
    verification_status: str = "supported"  # supported, partially_supported, contradicted, insufficient_evidence
    confidence_score: float = 1.0
    source_qualities: Dict[str, SourceReliabilityScore] = Field(default_factory=dict)


class CompositeScoreBreakdown(BaseModel):
    relevance_component: float = 0.0
    source_reliability_component: float = 0.0
    temporal_relevance_component: float = 0.0
    agreement_component: float = 0.0
    coverage_component: float = 0.0
    formula_weights: Dict[str, float] = Field(default_factory=dict)
    final_composite_score: float = 0.0


class EvidenceIntelligenceReport(BaseModel):
    query: str
    synthesis_markdown: str
    grouped_claims: List[GroupedClaimEvidence] = Field(default_factory=list)
    evidence_coverage_percentage: float = 0.0
    supported_claims_count: int = 0
    contradicted_claims_count: int = 0
    unsupported_claims_count: int = 0
    is_insufficient_evidence: bool = False
    insufficient_evidence_reason: Optional[str] = None
    composite_evidence_score: float = 0.0
    score_breakdown: Optional[CompositeScoreBreakdown] = None
    source_reliability_matrix: Dict[str, SourceReliabilityScore] = Field(default_factory=dict)
    retrieved_chunks: List[ScoredChunk] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    model_used: str = "evidence_intelligence_v1"


# ============================================================================
# PHASE 7 — SELF-CORRECTING RETRIEVAL ENGINE MODELS
# ============================================================================

class SelfCorrectionDecision(str, Enum):
    GENERATE = "generate"
    RETRY_MISSING_EVIDENCE = "retry_missing_evidence"
    RETRY_RESOLVE_CONTRADICTION = "retry_resolve_contradiction"
    ABSTAIN = "abstain"


class RetrievalQualityScore(BaseModel):
    overall_quality: float = 0.0
    relevance_score: float = 0.0
    coverage_score: float = 0.0
    source_quality_score: float = 0.0
    redundancy_score: float = 0.0
    has_contradictions: bool = False
    missing_gaps: List[str] = Field(default_factory=list)
    recommended_decision: SelfCorrectionDecision = SelfCorrectionDecision.GENERATE
    evaluation_reason: str = ""


class SelfCorrectionIteration(BaseModel):
    iteration_number: int = 1
    search_query: str
    rewrite_strategy: Optional[str] = None
    retrieved_chunks_count: int = 0
    accumulated_chunks_count: int = 0
    quality_evaluation: Optional[RetrievalQualityScore] = None
    decision_taken: str = "generate"
    notes: Optional[str] = None


class VerifiedClaimItem(BaseModel):
    claim_text: str
    status: str = "supported"  # supported, unsupported, contradicted
    confidence: float = 1.0
    supporting_citations: List[EvidenceCitation] = Field(default_factory=list)
    verification_note: Optional[str] = None


class AnswerVerificationResult(BaseModel):
    raw_answer: str
    final_answer: str
    extracted_claims: List[str] = Field(default_factory=list)
    verified_claim_items: List[VerifiedClaimItem] = Field(default_factory=list)
    supported_claims_count: int = 0
    unsupported_claims_count: int = 0
    contradicted_claims_count: int = 0
    unsupported_claim_rate: float = 0.0
    was_regenerated: bool = False
    regeneration_reason: Optional[str] = None


class SelfCorrectingRAGResult(BaseModel):
    query: str
    final_answer_markdown: str
    status: str = "first_pass_success"  # first_pass_success, recovered, abstained
    total_iterations: int = 1
    max_iterations_allowed: int = 3
    iterations_trace: List[SelfCorrectionIteration] = Field(default_factory=list)
    accumulated_chunks: List[ScoredChunk] = Field(default_factory=list)
    verification: Optional[AnswerVerificationResult] = None
    final_evidence_coverage: float = 0.0
    is_abstained: bool = False
    abstention_reason: Optional[str] = None
    execution_time_ms: float = 0.0
    metrics: Dict[str, Any] = Field(default_factory=dict)
    model_used: str = "self_correcting_rag_v1"


# ============================================================================
# PHASE 8 — MULTIMODAL EVIDENCE ENGINE MODELS
# ============================================================================

class ModalityType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"
    CHART = "chart"
    IMAGE = "image"
    CODE = "code"


class TableData(BaseModel):
    table_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    num_rows: int = 0
    num_cols: int = 0
    caption: Optional[str] = None
    source_page: Optional[int] = None
    markdown_repr: str = ""


class ChartFigureData(BaseModel):
    figure_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    caption: Optional[str] = None
    figure_type: str = "chart"  # chart, diagram, architecture, plot, scan
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    visible_values: List[str] = Field(default_factory=list)
    explanatory_text: Optional[str] = None
    source_page: Optional[int] = None
    image_url: Optional[str] = None


class ImageData(BaseModel):
    image_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_type: str = "scan"  # scan, photo, diagram, screenshot
    ocr_text: Optional[str] = None
    caption: Optional[str] = None
    source_page: Optional[int] = None
    image_format: str = "png"


class CodeBlockData(BaseModel):
    code_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    language: str = "python"
    code_content: str
    source_file: Optional[str] = None
    source_page: Optional[int] = None


class MultimodalDocumentRepresentation(BaseModel):
    document_id: str
    filename: str
    text_chunks: List[DocumentChunk] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    figures: List[ChartFigureData] = Field(default_factory=list)
    images: List[ImageData] = Field(default_factory=list)
    code_blocks: List[CodeBlockData] = Field(default_factory=list)
    metadata: DocumentMetadata
    references: List[str] = Field(default_factory=list)


class MultimodalEvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    modality: ModalityType = ModalityType.TEXT
    document_id: str
    document_filename: str
    page_number: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    content_snippet: str
    table_data: Optional[TableData] = None
    chart_data: Optional[ChartFigureData] = None
    image_data: Optional[ImageData] = None
    code_data: Optional[CodeBlockData] = None
    relevance_score: float = 0.0
    provenance_label: str  # e.g. "Figure 3 • Paper.pdf • Page 12"


class MultimodalRetrievalResult(BaseModel):
    query: str
    synthesis_markdown: str
    evidence_items: List[MultimodalEvidenceItem] = Field(default_factory=list)
    modality_counts: Dict[str, int] = Field(default_factory=dict)
    overall_confidence: float = 0.0
    execution_time_ms: float = 0.0
    model_used: str = "multimodal_evidence_v1"


# ============================================================================
# PHASE 9 — NEXUS RESEARCH AGENT MODELS
# ============================================================================

class ResearchSubQuestion(BaseModel):
    id: str = Field(default_factory=lambda: f"sq-{uuid.uuid4().hex[:6]}")
    question: str
    priority: int = 1
    status: str = "pending"  # pending, in_progress, answered, partial_gap
    retrieved_evidence_ids: List[str] = Field(default_factory=list)
    key_findings_summary: Optional[str] = None


class ResearchPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:6]}")
    goal: str
    sub_questions: List[ResearchSubQuestion] = Field(default_factory=list)
    identified_entities: List[str] = Field(default_factory=list)
    key_hypotheses: List[str] = Field(default_factory=list)
    strategy_overview: str = ""


class ResearchActionStep(BaseModel):
    step_number: int
    action_type: str  # planning, graph_traversal, hybrid_search, evidence_analysis, gap_detection, verification, synthesis
    description: str
    status: str = "completed"  # in_progress, completed, skipped, failed
    timestamp_ms: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)


class SourceTableRow(BaseModel):
    source_filename: str
    source_type: str = "Academic Paper"
    publication_date: Optional[str] = None
    relevance_score: float = 0.0
    reliability_score: float = 0.0
    used_claims_count: int = 0
    provenance_page: Optional[int] = 1


class ResearchBudgetTelemetry(BaseModel):
    total_tokens_estimated: int = 0
    searches_executed: int = 0
    retrieval_calls: int = 0
    graph_queries_executed: int = 0
    llm_calls_made: int = 0
    execution_time_seconds: float = 0.0
    budget_limit_reached: bool = False
    termination_reason: str = "goal_completed"  # goal_completed, max_iterations_reached, budget_limit_reached, max_time_reached


class ResearchGoalRequest(BaseModel):
    goal: str
    max_iterations: int = 3
    max_searches: int = 8
    max_time_seconds: int = 30
    enable_graph_traversal: bool = True
    enable_contradiction_detection: bool = True


class ResearchAgentReportResult(BaseModel):
    goal: str
    plan: ResearchPlan
    report_markdown: str
    source_table: List[SourceTableRow] = Field(default_factory=list)
    action_trace: List[ResearchActionStep] = Field(default_factory=list)
    contradictions_found: List[Dict[str, Any]] = Field(default_factory=list)
    telemetry: ResearchBudgetTelemetry
    confidence_score: float = 0.0
    model_used: str = "nexus_research_agent_v1"





