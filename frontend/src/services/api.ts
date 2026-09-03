import {
  DocumentInfo,
  DocumentChunk,
  ScoredChunk,
  EvidenceSynthesisResult,
  SystemStatus,
  QueryConfig,
  QueryAnalysis,
  BenchmarkReport,
  RetrievalPlan,
  PlanStep,
  TemporalDiffResult,
  TemporalConflictResult,
  TemporalFilter,
} from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export const api = {
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE_URL}/system/status`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Status check failed: ${res.statusText}`);
    return res.json();
  },

  async listDocuments(): Promise<DocumentInfo[]> {
    const res = await fetch(`${API_BASE_URL}/documents`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to list documents: ${res.statusText}`);
    return res.json();
  },

  async getDocument(docId: string): Promise<DocumentInfo> {
    const res = await fetch(`${API_BASE_URL}/documents/${docId}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to get document: ${res.statusText}`);
    return res.json();
  },

  async getDocumentChunks(docId: string): Promise<DocumentChunk[]> {
    const res = await fetch(`${API_BASE_URL}/documents/${docId}/chunks`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to load chunks: ${res.statusText}`);
    return res.json();
  },

  async uploadDocument(file: File): Promise<{ document_id: string; filename: string; chunk_count: number }> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async deleteDocument(docId: string): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE_URL}/documents/${docId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error(`Delete failed: ${res.statusText}`);
    return res.json();
  },

  async generatePlan(query: string): Promise<RetrievalPlan> {
    const res = await fetch(`${API_BASE_URL}/reasoning/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error(`Plan generation failed: ${res.statusText}`);
    return res.json();
  },

  async executeMultiHopReasoning(query: string): Promise<EvidenceSynthesisResult> {
    const res = await fetch(`${API_BASE_URL}/reasoning/multihop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Multi-hop reasoning failed");
    }
    return res.json();
  },

  async queryTemporal(req: {
    query: string;
    as_of_date?: string;
    start_date?: string;
    end_date?: string;
    version?: string;
    latest_only?: boolean;
    top_k?: number;
  }): Promise<EvidenceSynthesisResult> {
    const res = await fetch(`${API_BASE_URL}/temporal/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error(`Temporal query failed: ${res.statusText}`);
    return res.json();
  },

  async diffTemporal(topic: string, period_from: string, period_to: string): Promise<TemporalDiffResult> {
    const res = await fetch(`${API_BASE_URL}/temporal/diff`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, period_from, period_to }),
    });
    if (!res.ok) throw new Error(`Temporal diff failed: ${res.statusText}`);
    return res.json();
  },

  async checkConflict(req: any): Promise<TemporalConflictResult> {
    const res = await fetch(`${API_BASE_URL}/temporal/conflict-check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error(`Conflict check failed: ${res.statusText}`);
    return res.json();
  },

  async runReasoningBenchmark(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/reasoning/benchmark`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`Reasoning benchmark failed: ${res.statusText}`);
    return res.json();
  },

  async analyzeQuery(query: string): Promise<QueryAnalysis> {
    const res = await fetch(`${API_BASE_URL}/query/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error(`Query analysis failed: ${res.statusText}`);
    return res.json();
  },

  async runEvaluationBenchmark(): Promise<BenchmarkReport> {
    const res = await fetch(`${API_BASE_URL}/evaluation/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Evaluation benchmark failed");
    }
    return res.json();
  },

  async searchRetrieval(query: string, config: QueryConfig): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/query/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, ...config }),
    });
    if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
    return res.json();
  },

  async synthesizeEvidence(query: string, config: QueryConfig): Promise<EvidenceSynthesisResult> {
    const res = await fetch(`${API_BASE_URL}/query/synthesize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, ...config }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Synthesis failed");
    }
    return res.json();
  },
};
