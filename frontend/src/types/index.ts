export interface DocumentMetadata {
  title?: string;
  author?: string;
  file_type: string;
  file_size: number;
  page_count?: number;
  created_at: string;
}

export interface ChunkSpan {
  start_char: number;
  end_char: number;
  page_number?: number;
  section_title?: string;
}

export interface ChunkSpan {
  start_char: number;
  end_char: number;
  page_number?: number;
  section_title?: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  start_char?: number;
  end_char?: number;
  page_number?: number;
  section_title?: string;
  span?: ChunkSpan;
  version?: string;
  valid_from?: string;
  valid_until?: string;
  is_latest?: boolean;
  metadata?: Record<string, any>;
}

export interface ScoredChunk {
  chunk: DocumentChunk;
  dense_score?: number;
  dense_rank?: number;
  sparse_score?: number;
  sparse_rank?: number;
  rrf_score?: number;
  rerank_score?: number;
  final_score: number;
}

export interface EvidenceCitation {
  citation_id: string;
  chunk_id: string;
  document_id: string;
  document_filename: string;
  page_number?: number;
  section_title?: string;
  exact_quote: string;
  relevance_score: number;
  version?: string;
  valid_from?: string;
  valid_until?: string;
  is_latest?: boolean;
}

export interface EvidenceClaim {
  claim_id: string;
  statement: string;
  supporting_citations: EvidenceCitation[];
  confidence_score: number;
  verification_status: "supported" | "partially_supported" | "unverified" | "contradiction";
}

export type QueryCategory =
  | "simple_factual"
  | "semantic"
  | "comparative"
  | "temporal"
  | "multi_hop"
  | "analytical"
  | "research";

export interface PlanStep {
  step_number: number;
  sub_query: string;
  retrieval_strategy: string;
  depends_on_step?: number | null;
  expected_output_entity?: string | null;
  description?: string | null;
  status: "pending" | "in_progress" | "completed" | "failed";
}

export interface RetrievalPlan {
  plan_id: string;
  original_query: string;
  query_category: QueryCategory;
  reasoning_summary: string;
  steps: PlanStep[];
  estimated_hops: number;
  is_multihop: boolean;
}

export interface StepEvidence {
  step_number: number;
  sub_query: string;
  retrieved_chunks: ScoredChunk[];
  extracted_facts: string[];
  discovered_entities: string[];
  confidence_score: number;
  was_rewritten: boolean;
  original_sub_query?: string | null;
  execution_time_ms: number;
}

export interface MultiHopReasoningTrace {
  plan: RetrievalPlan;
  step_evidences: StepEvidence[];
  total_hops_executed: number;
  stop_reason: string;
  all_accumulated_chunks: ScoredChunk[];
  total_reasoning_time_ms: number;
}

export interface TemporalFilter {
  as_of_date?: string;
  start_date?: string;
  end_date?: string;
  version?: string;
  latest_only: boolean;
}

export interface TemporalClaimDiff {
  attribute: string;
  prior_state: string;
  prior_date: string;
  current_state: string;
  current_date: string;
  change_type: string;
  explanation: string;
}

export interface TemporalDiffResult {
  topic: string;
  period_from: string;
  period_to: string;
  diff_summary: string;
  detected_changes: TemporalClaimDiff[];
  confidence: number;
}

export interface TemporalConflictResult {
  claim_a: string;
  claim_b: string;
  timestamp_a?: string;
  timestamp_b?: string;
  document_a?: string;
  document_b?: string;
  conflict_type: "genuine_contradiction" | "version_change" | "temporal_evolution" | "unrelated";
  explanation: string;
  confidence: number;
}

export interface EvidenceSynthesisResult {
  query: string;
  synthesis_markdown: string;
  claims: EvidenceClaim[];
  retrieved_chunks: ScoredChunk[];
  overall_confidence: number;
  source_reliability_matrix: Record<string, number>;
  retrieval_trace?: RetrievalTrace;
  multihop_trace?: MultiHopReasoningTrace;
  temporal_diff?: TemporalDiffResult;
  execution_time_ms: number;
  model_used: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count?: number;
  chunk_count: number;
  created_at: string;
  updated_at?: string;
  published_at?: string;
  valid_from?: string;
  valid_until?: string;
  version?: string;
  lineage_id?: string;
  is_latest?: boolean;
  superseded_by?: string;
  title?: string;
  author?: string;
  tags?: string[];
  local_path?: string;
  content_preview?: string;
}

export interface SystemStatus {
  project_name: string;
  version: string;
  environment: string;
  llm_provider: string;
  embedding_provider: string;
  embedding_model?: string;
  embedding_dimension?: number;
  reranker_provider: string;
  reranker_model?: string;
  total_documents: number;
  total_chunks: number;
  status: string;
}


export interface QueryConfig {
  use_dense: boolean;
  use_sparse: boolean;
  use_reranker: boolean;
  dense_weight: number;
  sparse_weight: number;
  top_k: number;
  rerank_top_k: number;
  selected_document_ids?: string[];
}

export interface ExtractedConstraints {
  date_after?: string;
  date_before?: string;
  target_documents: string[];
  target_authors: string[];
  target_file_types: string[];
  tags: string[];
}

export interface QueryAnalysis {
  original_query: string;
  cleaned_query: string;
  intent: string;
  keywords: string[];
  entities: string[];
  constraints: ExtractedConstraints;
  suggested_retrieval_mode: string;
}

export interface StageCandidate {
  chunk_id: string;
  document_filename: string;
  page_number?: number;
  score: number;
  rank: number;
  content_snippet: string;
}

export interface RetrievalTrace {
  query: string;
  query_analysis?: QueryAnalysis;
  vector_candidates_count: number;
  bm25_candidates_count: number;
  fused_candidates_count: number;
  reranked_candidates_count: number;
  stage_latencies_ms: Record<string, number>;
  vector_top_candidates: StageCandidate[];
  bm25_top_candidates: StageCandidate[];
  fused_top_candidates: StageCandidate[];
  final_ranked_candidates: StageCandidate[];
  total_pipeline_time_ms: number;
}

export interface EvaluationMetricScores {
  recall_at_1: number;
  recall_at_3: number;
  recall_at_5: number;
  recall_at_10: number;
  precision_at_1: number;
  precision_at_3: number;
  precision_at_5: number;
  precision_at_10: number;
  mrr: number;
  ndcg_at_5: number;
  ndcg_at_10: number;
}

export interface MethodBenchmarkResult {
  method_name: string;
  description: string;
  metrics: EvaluationMetricScores;
  average_latency_ms: number;
}

export interface BenchmarkReport {
  benchmark_timestamp: string;
  total_test_queries: number;
  corpus_documents_count: number;
  corpus_chunks_count: number;
  results_by_method: Record<string, MethodBenchmarkResult>;
  hybrid_superiority_delta: Record<string, number>;
}

export interface AppSettings {
  llmProvider: string;
  llmModel: string;
  embeddingProvider: string;
  embeddingModel: string;
  rerankerProvider: string;
  chunkSize: number;
  chunkOverlap: number;
  defaultTopK: number;
}

// ============================================================================
// PHASE 5 — KNOWLEDGE GRAPH INTELLIGENCE TYPES
// ============================================================================

export type EntityType =
  | "person"
  | "organization"
  | "company"
  | "technology"
  | "model"
  | "paper"
  | "dataset"
  | "concept"
  | "event"
  | "product"
  | "location"
  | "date";

export type RelationshipType =
  | "AUTHORED_BY"
  | "CREATED_BY"
  | "USES"
  | "DEPENDS_ON"
  | "INTRODUCED"
  | "EVALUATED_ON"
  | "COMPETES_WITH"
  | "RELATED_TO"
  | "PRECEDED_BY"
  | "SUCCEEDED_BY"
  | "AFFILIATED_WITH"
  | "PART_OF"
  | "TRAINED_ON";

export interface GraphProvenance {
  document_id: string;
  document_filename: string;
  chunk_id: string;
  page_number?: number;
  section_title?: string;
  exact_snippet: string;
  confidence: number;
  extracted_at?: string;
}

export interface EntityNode {
  id: string;
  canonical_name: string;
  entity_type: EntityType;
  aliases: string[];
  description?: string;
  mention_count: number;
  provenance_list: GraphProvenance[];
  properties?: Record<string, any>;
  created_at?: string;
}

export interface RelationshipEdge {
  id: string;
  source_id: string;
  source_name: string;
  target_id: string;
  target_name: string;
  relationship_type: RelationshipType;
  description?: string;
  weight: number;
  provenance_list: GraphProvenance[];
  properties?: Record<string, any>;
  created_at?: string;
}

export interface KnowledgeGraphSubgraph {
  nodes: EntityNode[];
  edges: RelationshipEdge[];
  query_entity_id?: string;
  depth: number;
  total_nodes: number;
  total_edges: number;
}

export interface GraphPath {
  nodes: EntityNode[];
  edges: RelationshipEdge[];
  path_description: string;
  hops: number;
}

export interface GraphStats {
  total_entities: number;
  total_relationships: number;
  entity_types_count: Record<string, number>;
  relationship_types_count: Record<string, number>;
  storage_engine: string;
  connected: boolean;
}

export interface HybridGraphQueryRequest {
  query: string;
  top_k?: number;
  max_graph_hops?: number;
  graph_boost_factor?: number;
  use_dense?: boolean;
  use_sparse?: boolean;
  use_reranker?: boolean;
}

export interface HybridGraphRAGResult {
  query: string;
  synthesis_markdown: string;
  claims: EvidenceClaim[];
  retrieved_chunks: ScoredChunk[];
  graph_entities: EntityNode[];
  graph_relationships: RelationshipEdge[];
  graph_paths: GraphPath[];
  subgraph?: KnowledgeGraphSubgraph;
  overall_confidence: number;
  execution_time_ms: number;
  model_used: string;
}

// ============================================================================
// PHASE 6 — EVIDENCE INTELLIGENCE ENGINE TYPES
// ============================================================================

export type NLIClassificationType =
  | "entailment"
  | "contradiction"
  | "partial_contradiction"
  | "different_conditions"
  | "temporal_difference"
  | "neutral";

export interface NLIResult {
  premise: string;
  hypothesis: string;
  verdict: NLIClassificationType;
  confidence: number;
  explanation: string;
  condition_a?: string;
  condition_b?: string;
  metric_diff?: string;
}

export interface SourceReliabilityScore {
  document_filename: string;
  overall_score: number;
  source_type_score: number;
  authority_score: number;
  recency_score: number;
  corroboration_score: number;
  citation_quality_score: number;
  document_type: string;
  explanation: string;
}

export interface GroupedClaimEvidence {
  claim_id: string;
  statement: string;
  supporting_citations: EvidenceCitation[];
  contradicting_citations: EvidenceCitation[];
  conflict_explanation?: string;
  has_conflict: boolean;
  verification_status: "supported" | "partially_supported" | "contradicted" | "insufficient_evidence";
  confidence_score: number;
  source_qualities: Record<string, SourceReliabilityScore>;
}

export interface CompositeScoreBreakdown {
  relevance_component: number;
  source_reliability_component: number;
  temporal_relevance_component: number;
  agreement_component: number;
  coverage_component: number;
  formula_weights: Record<string, number>;
  final_composite_score: number;
}

export interface EvidenceIntelligenceReport {
  query: string;
  synthesis_markdown: string;
  grouped_claims: GroupedClaimEvidence[];
  evidence_coverage_percentage: number;
  supported_claims_count: number;
  contradicted_claims_count: number;
  unsupported_claims_count: number;
  is_insufficient_evidence: boolean;
  insufficient_evidence_reason?: string;
  composite_evidence_score: number;
  score_breakdown?: CompositeScoreBreakdown;
  source_reliability_matrix: Record<string, SourceReliabilityScore>;
  retrieved_chunks: ScoredChunk[];
  execution_time_ms: number;
  model_used: string;
}

// ============================================================================
// PHASE 7 — SELF-CORRECTING RETRIEVAL ENGINE TYPES
// ============================================================================

export type SelfCorrectionDecision =
  | "generate"
  | "retry_missing_evidence"
  | "retry_resolve_contradiction"
  | "abstain";

export interface RetrievalQualityScore {
  overall_quality: number;
  relevance_score: number;
  coverage_score: number;
  source_quality_score: number;
  redundancy_score: number;
  has_contradictions: boolean;
  missing_gaps: string[];
  recommended_decision: SelfCorrectionDecision;
  evaluation_reason: string;
}

export interface SelfCorrectionIteration {
  iteration_number: number;
  search_query: string;
  rewrite_strategy?: string;
  retrieved_chunks_count: number;
  accumulated_chunks_count: number;
  quality_evaluation?: RetrievalQualityScore;
  decision_taken: string;
  notes?: string;
}

export interface VerifiedClaimItem {
  claim_text: string;
  status: "supported" | "unsupported" | "contradicted";
  confidence: number;
  supporting_citations: EvidenceCitation[];
  verification_note?: string;
}

export interface AnswerVerificationResult {
  raw_answer: string;
  final_answer: string;
  extracted_claims: string[];
  verified_claim_items: VerifiedClaimItem[];
  supported_claims_count: number;
  unsupported_claims_count: number;
  contradicted_claims_count: number;
  unsupported_claim_rate: number;
  was_regenerated: boolean;
  regeneration_reason?: string;
}

export interface SelfCorrectingRAGResult {
  query: string;
  final_answer_markdown: string;
  status: "first_pass_success" | "recovered" | "abstained";
  total_iterations: number;
  max_iterations_allowed: number;
  iterations_trace: SelfCorrectionIteration[];
  accumulated_chunks: ScoredChunk[];
  verification?: AnswerVerificationResult;
  final_evidence_coverage: number;
  is_abstained: boolean;
  abstention_reason?: string;
  execution_time_ms: number;
  metrics: Record<string, any>;
  model_used: string;
}

// ============================================================================
// PHASE 8 — MULTIMODAL EVIDENCE ENGINE TYPES
// ============================================================================

export type ModalityType = "text" | "table" | "figure" | "chart" | "image" | "code";

export interface TableData {
  table_id: string;
  headers: string[];
  rows: string[][];
  num_rows: number;
  num_cols: number;
  caption?: string;
  source_page?: number;
  markdown_repr: string;
}

export interface ChartFigureData {
  figure_id: string;
  title?: string;
  caption?: string;
  figure_type: "chart" | "diagram" | "architecture" | "plot" | "scan" | "figure";
  x_axis_label?: string;
  y_axis_label?: string;
  visible_values: string[];
  explanatory_text?: string;
  source_page?: number;
  image_url?: string;
}

export interface ImageData {
  image_id: string;
  image_type: "scan" | "photo" | "diagram" | "screenshot";
  ocr_text?: string;
  caption?: string;
  source_page?: number;
  image_format: string;
}

export interface CodeBlockData {
  code_id: string;
  language: string;
  code_content: string;
  source_file?: string;
  source_page?: number;
}

export interface MultimodalDocumentRepresentation {
  document_id: string;
  filename: string;
  text_chunks: DocumentChunk[];
  tables: TableData[];
  figures: ChartFigureData[];
  images: ImageData[];
  code_blocks: CodeBlockData[];
  metadata: DocumentMetadata;
  references: string[];
}

export interface MultimodalEvidenceItem {
  evidence_id: string;
  modality: ModalityType;
  document_id: string;
  document_filename: string;
  page_number?: number;
  title?: string;
  caption?: string;
  content_snippet: string;
  table_data?: TableData;
  chart_data?: ChartFigureData;
  image_data?: ImageData;
  code_data?: CodeBlockData;
  relevance_score: number;
  provenance_label: string;
}

export interface MultimodalRetrievalResult {
  query: string;
  synthesis_markdown: string;
  evidence_items: MultimodalEvidenceItem[];
  modality_counts: Record<string, number>;
  overall_confidence: number;
  execution_time_ms: number;
  model_used: string;
}

// ============================================================================
// PHASE 9 — NEXUS RESEARCH AGENT TYPES
// ============================================================================

export interface ResearchSubQuestion {
  id: string;
  question: string;
  priority: number;
  status: "pending" | "in_progress" | "answered" | "partial_gap";
  retrieved_evidence_ids: string[];
  key_findings_summary?: string;
}

export interface ResearchPlan {
  plan_id: string;
  goal: string;
  sub_questions: ResearchSubQuestion[];
  identified_entities: string[];
  key_hypotheses: string[];
  strategy_overview: string;
}

export interface ResearchActionStep {
  step_number: number;
  action_type: "planning" | "graph_traversal" | "hybrid_search" | "evidence_analysis" | "gap_detection" | "verification" | "synthesis";
  description: string;
  status: "in_progress" | "completed" | "skipped" | "failed";
  timestamp_ms: number;
  details: Record<string, any>;
}

export interface SourceTableRow {
  source_filename: string;
  source_type: string;
  publication_date?: string;
  relevance_score: number;
  reliability_score: number;
  used_claims_count: number;
  provenance_page?: number;
}

export interface ResearchBudgetTelemetry {
  total_tokens_estimated: number;
  searches_executed: number;
  retrieval_calls: number;
  graph_queries_executed: number;
  llm_calls_made: number;
  execution_time_seconds: number;
  budget_limit_reached: boolean;
  termination_reason: "goal_completed" | "max_iterations_reached" | "budget_limit_reached" | "max_time_reached";
}

export interface ResearchGoalRequest {
  goal: string;
  max_iterations?: number;
  max_searches?: number;
  max_time_seconds?: number;
  enable_graph_traversal?: boolean;
  enable_contradiction_detection?: boolean;
}

export interface ResearchAgentReportResult {
  goal: string;
  plan: ResearchPlan;
  report_markdown: string;
  source_table: SourceTableRow[];
  action_trace: ResearchActionStep[];
  contradictions_found: Record<string, any>[];
  telemetry: ResearchBudgetTelemetry;
  confidence_score: number;
  model_used: string;
}

// ============================================================================
// AUTHENTICATION & MULTI-TENANCY TYPES
// ============================================================================

export interface UserAccount {
  user_id: string;
  username: string;
  name?: string;
  email: string;
  tenant_id: string;
  role: "admin" | "researcher" | "viewer";
  is_active: boolean;
  created_at?: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: UserAccount;
}




