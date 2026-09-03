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
  UserAccount,
  AuthTokenResponse,
} from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

let currentAuthToken: string | null = null;

export const api = {
  setAuthToken(token: string | null) {
    currentAuthToken = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("nexus_auth_token", token);
      } else {
        localStorage.removeItem("nexus_auth_token");
      }
    }
  },

  getAuthToken(): string | null {
    if (!currentAuthToken && typeof window !== "undefined") {
      currentAuthToken = localStorage.getItem("nexus_auth_token");
    }
    return currentAuthToken;
  },

  getHeaders(customHeaders: Record<string, string> = {}): HeadersInit {
    const token = this.getAuthToken();
    const headers: Record<string, string> = {
      ...customHeaders,
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  },

  // ==========================================================================
  // AUTHENTICATION API METHODS
  // ==========================================================================

  async login(usernameOrEmail: string, password: string): Promise<AuthTokenResponse> {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: usernameOrEmail, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Invalid credentials");
    }
    const data: AuthTokenResponse = await res.json();
    this.setAuthToken(data.access_token);
    return data;
  },

  async register(username: string, email: string, password: string, name?: string): Promise<AuthTokenResponse> {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password, name }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Registration failed");
    }
    const data: AuthTokenResponse = await res.json();
    this.setAuthToken(data.access_token);
    return data;
  },

  async getMe(): Promise<UserAccount> {
    const token = this.getAuthToken();
    const headers = this.getHeaders();
    const res = await fetch(`${API_BASE_URL}/auth/me?token=${token || ""}`, {
      headers,
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  async forgotPassword(email: string): Promise<{ status: string; message: string; reset_token?: string }> {
    const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    if (!res.ok) throw new Error("Failed to process password recovery request");
    return res.json();
  },

  async resetPassword(token: string, newPassword: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Reset failed" }));
      throw new Error(err.detail || "Password reset failed");
    }
    return res.json();
  },

  async logout(): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, { method: "POST" });
    } catch {}
    this.setAuthToken(null);
  },

  // ==========================================================================
  // SYSTEM & DOCUMENTS
  // ==========================================================================

  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE_URL}/system/status`, {
      headers: this.getHeaders(),
      cache: "no-store",
    });
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

  // ==========================================================================
  // PHASE 5 — KNOWLEDGE GRAPH API METHODS
  // ==========================================================================

  async getGraphStats(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/stats`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to load graph stats: ${res.statusText}`);
    return res.json();
  },

  async getGraphSchema(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/schema`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to load graph schema: ${res.statusText}`);
    return res.json();
  },

  async searchEntities(query: string = "", entity_type?: string, limit: number = 50): Promise<any[]> {
    const params = new URLSearchParams();
    if (query) params.append("query", query);
    if (entity_type && entity_type !== "all") params.append("entity_type", entity_type);
    params.append("limit", limit.toString());

    const res = await fetch(`${API_BASE_URL}/graph/entities?${params.toString()}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to search entities: ${res.statusText}`);
    return res.json();
  },

  async getEntityDetails(entityId: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/entities/${entityId}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to get entity: ${res.statusText}`);
    return res.json();
  },

  async getEntityNeighborhood(entityId: string, depth: number = 1): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/neighborhood/${entityId}?depth=${depth}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`Failed to load neighborhood: ${res.statusText}`);
    return res.json();
  },

  async executeHybridGraphRAG(req: any): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Hybrid Graph RAG query failed");
    }
    return res.json();
  },

  async extractGraphFromText(text: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error(`Ad-hoc extraction failed: ${res.statusText}`);
    return res.json();
  },

  async rebuildKnowledgeGraph(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/graph/build`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`Graph rebuild failed: ${res.statusText}`);
    return res.json();
  },

  async findEntityPaths(sourceName: string, targetName: string, maxDepth: number = 3): Promise<any[]> {
    const res = await fetch(`${API_BASE_URL}/graph/paths`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_name: sourceName, target_name: targetName, max_depth: maxDepth }),
    });
    if (!res.ok) throw new Error(`Path finding failed: ${res.statusText}`);
    return res.json();
  },

  // ==========================================================================
  // PHASE 6 — EVIDENCE INTELLIGENCE API METHODS
  // ==========================================================================

  async analyzeEvidence(query: string, config?: any): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/evidence/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, ...(config || {}) }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Evidence analysis failed");
    }
    return res.json();
  },

  async evaluateNLI(premise: string, hypothesis: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/evidence/nli`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ premise, hypothesis }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "NLI evaluation failed");
    }
    return res.json();
  },

  async evaluateSourceQuality(filename: string, content: string = ""): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/evidence/source-quality`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename, content }),
    });
    if (!res.ok) throw new Error(`Source quality evaluation failed: ${res.statusText}`);
    return res.json();
  },

  // ==========================================================================
  // PHASE 7 — SELF-CORRECTING RETRIEVAL ENGINE API METHODS
  // ==========================================================================

  async executeSelfCorrection(query: string, config?: any): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/self-correction/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, ...(config || {}) }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Self-correcting query failed");
    }
    return res.json();
  },

  async evaluateRetrievalQuality(query: string, chunkTexts: string[]): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/self-correction/evaluate-quality`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, chunk_texts: chunkTexts }),
    });
    if (!res.ok) throw new Error(`Quality evaluation failed: ${res.statusText}`);
    return res.json();
  },

  async verifyAnswerClaims(rawAnswer: string, evidenceTexts: string[]): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/self-correction/verify-answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_answer: rawAnswer, evidence_texts: evidenceTexts }),
    });
    if (!res.ok) throw new Error(`Answer verification failed: ${res.statusText}`);
    return res.json();
  },

  // ==========================================================================
  // PHASE 8 — MULTIMODAL EVIDENCE ENGINE API METHODS
  // ==========================================================================

  async queryMultimodalEvidence(query: string, requestedModality?: string, topK: number = 8): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/multimodal/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, requested_modality: requestedModality || "all", top_k: topK }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Multimodal query failed");
    }
    return res.json();
  },

  async parseMultimodalText(text: string, filename: string = "document.md"): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/multimodal/parse-text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, filename }),
    });
    if (!res.ok) throw new Error(`Multimodal parsing failed: ${res.statusText}`);
    return res.json();
  },

  async getDocumentStructure(documentId: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/multimodal/document/${documentId}/structure`);
    if (!res.ok) throw new Error(`Failed to fetch document structure: ${res.statusText}`);
    return res.json();
  },

  // ==========================================================================
  // PHASE 9 — NEXUS RESEARCH AGENT API METHODS
  // ==========================================================================

  async executeResearchAgent(params: {
    goal: string;
    max_iterations?: number;
    max_searches?: number;
    max_time_seconds?: number;
    enable_graph_traversal?: boolean;
    enable_contradiction_detection?: boolean;
  }): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/agent/research`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Research Agent execution failed");
    }
    return res.json();
  },

  async generateResearchPlan(goal: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/agent/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal }),
    });
    if (!res.ok) throw new Error(`Plan generation failed: ${res.statusText}`);
    return res.json();
  },
};





