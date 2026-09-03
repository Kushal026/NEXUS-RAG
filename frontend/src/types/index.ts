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
  reranker_provider: string;
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



