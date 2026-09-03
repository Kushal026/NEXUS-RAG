"use client";

import React, { useState } from "react";
import {
  Search,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  FileText,
  Clock,
  Cpu,
  Layers,
  ExternalLink,
  BookOpen,
  Scale
} from "lucide-react";
import {
  EvidenceSynthesisResult,
  QueryConfig,
  EvidenceClaim,
  EvidenceCitation,
  ScoredChunk,
} from "../../types";
import { api } from "../../services/api";

export const EvidenceWorkbench: React.FC = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [synthesis, setSynthesis] = useState<EvidenceSynthesisResult | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<EvidenceCitation | null>(null);

  const [config, setConfig] = useState<QueryConfig>({
    use_dense: true,
    use_sparse: true,
    use_reranker: true,
    dense_weight: 0.6,
    sparse_weight: 0.4,
    top_k: 10,
    rerank_top_k: 5,
  });

  const presetQueries = [
    "What are the core advantages of hybrid dense-sparse retrieval?",
    "How does Reciprocal Rank Fusion (RRF) balance keyword and vector search?",
    "Explain quantum superposition and neural network gradient descent.",
  ];

  const handleSearch = async (e?: React.FormEvent, searchOverride?: string) => {
    if (e) e.preventDefault();
    const queryText = searchOverride || query;
    if (!queryText.trim()) return;

    setLoading(true);
    setError(null);
    setSelectedCitation(null);

    try {
      const data = await api.synthesizeEvidence(queryText, config);
      setSynthesis(data);
    } catch (err: any) {
      setError(err.message || "Synthesis request failed.");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "supported":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" /> Supported
          </span>
        );
      case "partially_supported":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" /> Partially Supported
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20">
            Unverified
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Search & Configuration Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <form onSubmit={handleSearch} className="space-y-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask an analytical question or enter research hypothesis..."
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-sans"
              />
            </div>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-3 rounded-xl border text-xs font-medium flex items-center gap-1.5 transition-all ${
                showFilters
                  ? "bg-slate-800 text-indigo-400 border-indigo-500/40"
                  : "bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-850"
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span className="hidden sm:inline">Retrieval Tuning</span>
              {showFilters ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? "Synthesizing Evidence..." : "Investigate"}
            </button>
          </div>

          {/* Quick Preset Queries */}
          <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-400">
            <span className="text-[11px] text-slate-500">Preset Hypotheses:</span>
            {presetQueries.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(p);
                  handleSearch(undefined, p);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-950/80 border border-slate-800/80 hover:border-indigo-500/40 text-slate-300 text-[11px] truncate max-w-xs transition-all"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Collapsible Retrieval Tuning Drawer */}
          {showFilters && (
            <div className="pt-4 mt-2 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              <div className="space-y-1.5 p-3 rounded-xl bg-slate-950/60 border border-slate-850">
                <div className="flex justify-between text-slate-300">
                  <span>Dense Vector Weight</span>
                  <span className="font-mono text-indigo-400 font-bold">{config.dense_weight.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={config.dense_weight}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      dense_weight: parseFloat(e.target.value),
                      sparse_weight: Math.round((1 - parseFloat(e.target.value)) * 100) / 100,
                    })
                  }
                  className="w-full accent-indigo-500"
                />
              </div>

              <div className="space-y-1.5 p-3 rounded-xl bg-slate-950/60 border border-slate-850">
                <div className="flex justify-between text-slate-300">
                  <span>Sparse BM25 Weight</span>
                  <span className="font-mono text-cyan-400 font-bold">{config.sparse_weight.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={config.sparse_weight}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      sparse_weight: parseFloat(e.target.value),
                      dense_weight: Math.round((1 - parseFloat(e.target.value)) * 100) / 100,
                    })
                  }
                  className="w-full accent-cyan-500"
                />
              </div>

              <div className="space-y-1.5 p-3 rounded-xl bg-slate-950/60 border border-slate-850">
                <div className="flex justify-between text-slate-300">
                  <span>Top-K Fusion Candidates</span>
                  <span className="font-mono text-purple-400 font-bold">{config.top_k}</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="25"
                  step="1"
                  value={config.top_k}
                  onChange={(e) => setConfig({ ...config, top_k: parseInt(e.target.value) })}
                  className="w-full accent-purple-500"
                />
              </div>

              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 flex items-center justify-between">
                <div>
                  <label htmlFor="rerank-toggle" className="text-slate-200 font-medium cursor-pointer">
                    Cross-Encoder Reranking
                  </label>
                  <p className="text-[10px] text-slate-400">ms-marco neural scoring</p>
                </div>
                <input
                  type="checkbox"
                  id="rerank-toggle"
                  checked={config.use_reranker}
                  onChange={(e) => setConfig({ ...config, use_reranker: e.target.checked })}
                  className="w-4 h-4 rounded accent-indigo-600 cursor-pointer"
                />
              </div>
            </div>
          )}
        </form>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Synthesis & Evidence Dashboard */}
      {synthesis && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Synthesis & Claim Attribution */}
          <div className="lg:col-span-8 space-y-6">
            {/* Primary Synthesis Card */}
            <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                    Evidence Synthesis
                  </h3>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <span className="flex items-center gap-1 text-slate-400">
                    <Clock className="w-3.5 h-3.5" />
                    {synthesis.execution_time_ms} ms
                  </span>
                  <span className="flex items-center gap-1 text-slate-400 font-mono text-[11px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                    <Cpu className="w-3 h-3 text-cyan-400" />
                    {synthesis.model_used}
                  </span>
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                    <span>Confidence: {(synthesis.overall_confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Markdown Content */}
              <div className="text-sm text-slate-200 leading-relaxed space-y-3 font-sans whitespace-pre-wrap">
                {synthesis.synthesis_markdown}
              </div>
            </div>

            {/* Claim-Level Interactive Citations */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <Scale className="w-4 h-4 text-cyan-400" />
                  Verified Evidence Claims & Exact Citations ({synthesis.claims.length})
                </h4>
                <span className="text-xs text-slate-400">Click a citation to inspect passage span</span>
              </div>

              <div className="space-y-3">
                {synthesis.claims.map((claim) => (
                  <div
                    key={claim.claim_id}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-850 space-y-3 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-xs text-slate-100 font-medium leading-relaxed">
                        {claim.statement}
                      </p>
                      <div className="shrink-0 flex items-center gap-2">
                        {getStatusBadge(claim.verification_status)}
                        <span className="text-[11px] font-mono text-slate-400">
                          {(claim.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    {/* Supporting Citations */}
                    {claim.supporting_citations.length > 0 && (
                      <div className="space-y-1.5 pt-2 border-t border-slate-900">
                        {claim.supporting_citations.map((cit) => {
                          const isSelected = selectedCitation?.citation_id === cit.citation_id;
                          return (
                            <button
                              key={cit.citation_id}
                              onClick={() => setSelectedCitation(cit)}
                              className={`w-full text-left p-2.5 rounded-lg text-xs transition-all flex items-center justify-between gap-3 ${
                                isSelected
                                  ? "bg-indigo-950/60 border border-indigo-500/50 text-indigo-200"
                                  : "bg-slate-900/60 hover:bg-slate-900 text-slate-300 border border-slate-850"
                              }`}
                            >
                              <div className="flex items-center gap-2 truncate">
                                <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                                <span className="font-semibold text-slate-200 truncate">
                                  {cit.document_filename}
                                </span>
                                {cit.page_number && (
                                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                                    P. {cit.page_number}
                                  </span>
                                )}
                                <span className="text-slate-400 truncate italic">
                                  "{cit.exact_quote}"
                                </span>
                              </div>
                              <span className="font-mono text-[10px] text-emerald-400 font-semibold shrink-0">
                                Score: {cit.relevance_score.toFixed(3)}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Sidebar: Citation Inspector & Source Reliability Matrix */}
          <div className="lg:col-span-4 space-y-6">
            {/* Citation Inspector Drawer */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-indigo-400" />
                Citation Inspector
              </h4>

              {selectedCitation ? (
                <div className="space-y-3">
                  <div className="p-3.5 rounded-xl bg-slate-950 border border-indigo-500/30 space-y-2">
                    <div className="flex items-center justify-between text-[11px] text-slate-400 pb-1.5 border-b border-slate-850">
                      <span className="font-semibold text-slate-200 truncate">
                        {selectedCitation.document_filename}
                      </span>
                      {selectedCitation.page_number && (
                        <span className="text-cyan-400 font-mono">Page {selectedCitation.page_number}</span>
                      )}
                    </div>
                    <div className="text-xs text-indigo-300 bg-indigo-950/40 p-2.5 rounded-lg border border-indigo-900/60 font-mono">
                      "{selectedCitation.exact_quote}"
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400 pt-1">
                      <span>Relevance: {selectedCitation.relevance_score.toFixed(4)}</span>
                      <span className="font-mono truncate max-w-[120px]">Chunk: {selectedCitation.chunk_id}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-6 text-center text-xs text-slate-500 rounded-xl bg-slate-950/40 border border-slate-850">
                  Select any claim citation on the left to inspect its exact passage bounds and attribution.
                </div>
              )}
            </div>

            {/* Source Reliability Matrix */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Source Reliability Matrix
              </h4>

              <div className="space-y-2.5">
                {Object.entries(synthesis.source_reliability_matrix).map(([src, rel]) => (
                  <div key={src} className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-slate-200 truncate max-w-[180px]">{src}</span>
                      <span className="font-mono text-emerald-400 font-bold">{(rel * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${rel * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Retrieved Passages Overview */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                Retrieved Context Passages ({synthesis.retrieved_chunks.length})
              </h4>
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {synthesis.retrieved_chunks.map((sc, idx) => (
                  <div
                    key={sc.chunk.id}
                    className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-850 text-xs space-y-1"
                  >
                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span className="font-mono text-indigo-400 font-bold">
                        #{idx + 1} {sc.chunk.metadata?.filename || "Evidence Chunk"}
                      </span>
                      <span className="font-mono text-emerald-400">{sc.final_score.toFixed(3)}</span>
                    </div>
                    <p className="text-[11px] text-slate-300 line-clamp-2 font-mono">
                      {sc.chunk.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
