"use client";

import React, { useState } from "react";
import {
  Search,
  Sparkles,
  SlidersHorizontal,
  FileText,
  Clock,
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  Zap,
  Tag,
  Scale,
  RefreshCw,
  Filter,
  GitBranch
} from "lucide-react";
import {
  DocumentInfo,
  QueryConfig,
  EvidenceSynthesisResult,
  EvidenceCitation,
  ScoredChunk,
} from "../../types";
import { api } from "../../services/api";
import { RetrievalProcessWaterfall } from "../evidence/RetrievalProcessWaterfall";
import { ResearchReasoningTimeline } from "./ResearchReasoningTimeline";
import { TemporalTimelineBar } from "../temporal/TemporalTimelineBar";
import { TemporalDiffViewer } from "../temporal/TemporalDiffViewer";
import { TemporalFilter } from "../../types";

interface ResearchWorkbenchProps {
  documents: DocumentInfo[];
}

export const ResearchWorkbench: React.FC<ResearchWorkbenchProps> = ({ documents }) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [isMultiHopMode, setIsMultiHopMode] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [synthesis, setSynthesis] = useState<EvidenceSynthesisResult | null>(null);
  const [streamedText, setStreamedText] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [showWaterfall, setShowWaterfall] = useState(true);
  const [showTimeline, setShowTimeline] = useState(true);
  const [selectedCitation, setSelectedCitation] = useState<EvidenceCitation | null>(null);
  const [selectedDocFilter, setSelectedDocFilter] = useState<string>("all");
  const [temporalFilter, setTemporalFilter] = useState<TemporalFilter>({ latest_only: false });

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
    "What is the latest specification of the quantum cryogenic controller?",
    "What was the operating temperature as of 2023?",
    "What changed between 2024 and 2026?",
    "What techniques are used in NEXUS-7700-TX, who operates it, and how is cryogenic coherence maintained?",
    "Compare dense semantic vectors versus sparse BM25 retrieval and explain neural reranking.",
  ];

  const handleSearch = async (e?: React.FormEvent, searchOverride?: string) => {
    if (e) e.preventDefault();
    const queryText = searchOverride || query;
    if (!queryText.trim() || loading) return;

    setLoading(true);
    setError(null);
    setStreamedText("");
    setSynthesis(null);
    setSelectedCitation(null);

    try {
      // Check for temporal diff intent in query (e.g. "between 2024 and 2026")
      const diffMatch = queryText.match(/between\s+(\d{4})\s+and\s+(\d{4})/i);

      if (diffMatch) {
        const fromYear = diffMatch[1];
        const toYear = diffMatch[2];
        const [diffRes, synthRes] = await Promise.all([
          api.diffTemporal(queryText, fromYear, toYear).catch(() => null),
          api.queryTemporal({
            query: queryText,
            start_date: fromYear,
            end_date: toYear,
            top_k: config.top_k,
          }),
        ]);
        if (synthRes && diffRes) {
          synthRes.temporal_diff = diffRes;
        }
        setSynthesis(synthRes);
        setStreamedText(synthRes.synthesis_markdown);
      } else if (temporalFilter.as_of_date || temporalFilter.latest_only) {
        const result = await api.queryTemporal({
          query: queryText,
          as_of_date: temporalFilter.as_of_date,
          latest_only: temporalFilter.latest_only,
          top_k: config.top_k,
        });
        setSynthesis(result);
        setStreamedText(result.synthesis_markdown);
      } else if (isMultiHopMode) {
        const result = await api.executeMultiHopReasoning(queryText);
        setSynthesis(result);
        setStreamedText(result.synthesis_markdown);
      } else {
        const queryPayload = {
          ...config,
          metadata_filter: selectedDocFilter !== "all" ? { filename: selectedDocFilter } : undefined,
        };
        const result = await api.synthesizeEvidence(queryText, queryPayload);
        setSynthesis(result);
        setStreamedText(result.synthesis_markdown);
      }
    } catch (err: any) {
      setError(err.message || "Query execution failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Search Header & Filter Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <form onSubmit={handleSearch} className="space-y-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a complex multi-hop research question or query hypothesis..."
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-sans"
              />
            </div>

            {/* Document Filter Dropdown */}
            <div className="hidden sm:flex items-center bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs">
              <Filter className="w-3.5 h-3.5 text-slate-400 mr-2" />
              <select
                value={selectedDocFilter}
                onChange={(e) => setSelectedDocFilter(e.target.value)}
                className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
              >
                <option value="all" className="bg-slate-900 text-slate-200">
                  All Vault Sources ({documents.length})
                </option>
                {documents.map((d) => (
                  <option key={d.id} value={d.filename} className="bg-slate-900 text-slate-200">
                    {d.filename}
                  </option>
                ))}
              </select>
            </div>

            {/* Multi-Hop Mode Toggle */}
            <button
              type="button"
              onClick={() => setIsMultiHopMode(!isMultiHopMode)}
              className={`px-4 py-3 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
                isMultiHopMode
                  ? "bg-indigo-600/30 text-indigo-300 border-indigo-500 shadow-md shadow-indigo-500/20"
                  : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              <GitBranch className="w-4 h-4" />
              <span className="hidden sm:inline">Multi-Hop Reasoning</span>
            </button>

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
              <span className="hidden md:inline">Tuning</span>
              {showFilters ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? "Reasoning..." : "Investigate"}
            </button>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-400">
            <span className="text-[11px] text-slate-500">Suggested Hypotheses:</span>
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

          {/* Temporal Time-Travel Bar */}
          <TemporalTimelineBar
            temporalFilter={temporalFilter}
            onChange={(newF) => setTemporalFilter(newF)}
          />
        </form>

        {/* Collapsible Retrieval & Weights Tuning */}
        {showFilters && (
          <div className="pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-6 text-xs animate-fadeIn">
            {/* Retrieval Channel Toggles */}
            <div className="space-y-3">
              <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
                Active Search Channels
              </span>
              <div className="space-y-2">
                <label className="flex items-center gap-2.5 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={config.use_dense}
                    onChange={(e) => setConfig({ ...config, use_dense: e.target.checked })}
                    className="rounded bg-slate-950 border-slate-700 text-indigo-500 focus:ring-0"
                  />
                  <span>Dense Semantic Embeddings (pgvector)</span>
                </label>

                <label className="flex items-center gap-2.5 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={config.use_sparse}
                    onChange={(e) => setConfig({ ...config, use_sparse: e.target.checked })}
                    className="rounded bg-slate-950 border-slate-700 text-indigo-500 focus:ring-0"
                  />
                  <span>Sparse Lexical BM25 Search</span>
                </label>

                <label className="flex items-center gap-2.5 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={config.use_reranker}
                    onChange={(e) => setConfig({ ...config, use_reranker: e.target.checked })}
                    className="rounded bg-slate-950 border-slate-700 text-indigo-500 focus:ring-0"
                  />
                  <span>Neural Cross-Encoder Reranker</span>
                </label>
              </div>
            </div>

            {/* Fusion Weight Sliders */}
            <div className="space-y-3">
              <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
                Reciprocal Rank Fusion Weights
              </span>
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Dense Vector Weight:</span>
                    <span className="font-mono text-indigo-400">{config.dense_weight.toFixed(2)}</span>
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
                        sparse_weight: parseFloat((1 - parseFloat(e.target.value)).toFixed(2)),
                      })
                    }
                    className="w-full accent-indigo-500 bg-slate-950"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Sparse BM25 Weight:</span>
                    <span className="font-mono text-cyan-400">{config.sparse_weight.toFixed(2)}</span>
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
                        dense_weight: parseFloat((1 - parseFloat(e.target.value)).toFixed(2)),
                      })
                    }
                    className="w-full accent-cyan-500 bg-slate-950"
                  />
                </div>
              </div>
            </div>

            {/* Top-K Pools */}
            <div className="space-y-3">
              <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
                Candidate Pools & Budget
              </span>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Fused Pool Top-K:</span>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    value={config.top_k}
                    onChange={(e) => setConfig({ ...config, top_k: parseInt(e.target.value) || 10 })}
                    className="w-16 px-2 py-1 rounded bg-slate-950 border border-slate-800 text-right font-mono"
                  />
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Rerank Evidence Output:</span>
                  <input
                    type="number"
                    min="1"
                    max="15"
                    value={config.rerank_top_k}
                    onChange={(e) =>
                      setConfig({ ...config, rerank_top_k: parseInt(e.target.value) || 5 })
                    }
                    className="w-16 px-2 py-1 rounded bg-slate-950 border border-slate-800 text-right font-mono"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2 animate-fadeIn">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Evidence Workbench Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left / Top Main Column: Reasoning Timeline + Answer Synthesis + Claims */}
        <div className="lg:col-span-8 space-y-6">
          {/* Multi-Hop Research Reasoning Timeline */}
          {synthesis?.multihop_trace && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                  <GitBranch className="w-3.5 h-3.5" /> Research Reasoning Plan & Execution
                </span>
                <button
                  onClick={() => setShowTimeline(!showTimeline)}
                  className="text-xs text-slate-400 hover:text-slate-200"
                >
                  {showTimeline ? "Collapse Plan" : "Expand Plan Timeline"}
                </button>
              </div>
              {showTimeline && <ResearchReasoningTimeline trace={synthesis.multihop_trace} />}
            </div>
          )}

          {/* Temporal Evolution & Version Diff Card */}
          {synthesis?.temporal_diff && (
            <TemporalDiffViewer diffResult={synthesis.temporal_diff} />
          )}

          {/* Answer Synthesis Card */}
          {(loading || synthesis || streamedText) && (
            <div className="glass-panel-glow p-6 rounded-2xl border border-indigo-500/30 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <h3 className="text-sm font-bold text-white tracking-wide">
                    Evidence Synthesis & Attributed Findings
                  </h3>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  {synthesis && (
                    <>
                      <span className="flex items-center gap-1 text-slate-400 font-mono text-[11px]">
                        <Clock className="w-3.5 h-3.5" />
                        {synthesis.execution_time_ms} ms
                      </span>
                      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                        <span>Confidence: {(synthesis.overall_confidence * 100).toFixed(1)}%</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Rendered Markdown Content */}
              <div className="text-sm text-slate-200 leading-relaxed space-y-3 font-sans whitespace-pre-wrap">
                {streamedText || (
                  <div className="p-8 text-center text-slate-400 text-xs animate-pulse">
                    Executing multi-hop retrieval reasoning and compiling evidence...
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Retrieval Process Waterfall (5 Stages) */}
          {synthesis?.retrieval_trace && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Observability Trace Visualizer
                </span>
                <button
                  onClick={() => setShowWaterfall(!showWaterfall)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
                >
                  {showWaterfall ? "Collapse Process" : "Expand Process Waterfall"}
                </button>
              </div>
              {showWaterfall && <RetrievalProcessWaterfall trace={synthesis.retrieval_trace} />}
            </div>
          )}

          {/* Claim-Level Interactive Citations */}
          {synthesis && synthesis.claims.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <Scale className="w-4 h-4 text-cyan-400" />
                  Verified Evidence Claims & Exact Citations ({synthesis.claims.length})
                </h4>
                <span className="text-xs text-slate-400">Click a citation to inspect exact span</span>
              </div>

              <div className="space-y-3">
                {synthesis.claims.map((claim, cIdx) => (
                  <div
                    key={claim.claim_id}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-850 space-y-3 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-xs text-slate-100 font-medium leading-relaxed">
                        {claim.statement}
                      </p>
                      <span
                        className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full shrink-0 ${
                          claim.verification_status === "supported"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                        }`}
                      >
                        {claim.verification_status}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-2 pt-1">
                      {claim.supporting_citations?.map((cite, citIdx) => (
                        <button
                          key={citIdx}
                          onClick={() => setSelectedCitation(cite)}
                          className={`text-[11px] px-2.5 py-1 rounded-lg border font-mono transition-all flex items-center gap-1.5 ${
                            selectedCitation?.document_filename === cite.document_filename &&
                            selectedCitation?.chunk_id === cite.chunk_id
                              ? "bg-indigo-600 text-white border-indigo-400 shadow-md shadow-indigo-600/30"
                              : "bg-slate-900 border-slate-800 text-indigo-300 hover:border-indigo-500/50"
                          }`}
                        >
                          <FileText className="w-3 h-3 text-indigo-400" />
                          <span>
                            {cite.document_filename} {cite.page_number && `• P.${cite.page_number}`}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Evidence Inspector & Source Reliability Matrix */}
        <div className="lg:col-span-4 space-y-6">
          {/* Selected Citation Span Inspector */}
          {selectedCitation ? (
            <div className="glass-panel p-6 rounded-2xl border border-indigo-500/40 space-y-4 animate-fadeIn">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <ExternalLink className="w-3.5 h-3.5 text-indigo-400" /> Grounding Evidence Span
                </span>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">
                  {(selectedCitation.relevance_score * 100).toFixed(0)}% Match
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-slate-400">Document:</span>
                  <p className="font-semibold text-slate-200">{selectedCitation.document_filename}</p>
                </div>

                {selectedCitation.page_number && (
                  <div>
                    <span className="text-slate-400">Page:</span>
                    <p className="font-mono text-slate-200">Page {selectedCitation.page_number}</p>
                  </div>
                )}

                <div>
                  <span className="text-slate-400">Exact Excerpt Quote:</span>
                  <blockquote className="mt-1 p-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 font-serif italic text-xs leading-relaxed">
                    "{selectedCitation.exact_quote}"
                  </blockquote>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 text-center space-y-2">
              <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto" />
              <h5 className="text-xs font-semibold text-slate-300">Citation Span Inspector</h5>
              <p className="text-[11px] text-slate-500">
                Click any citation tag on the left to inspect exact source quotes and page boundaries.
              </p>
            </div>
          )}

          {/* Source Reliability Matrix */}
          {synthesis && Object.keys(synthesis.source_reliability_matrix).length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" /> Source Reliability Matrix
              </h4>

              <div className="space-y-3">
                {Object.entries(synthesis.source_reliability_matrix).map(([src, score]) => (
                  <div key={src} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 truncate max-w-[200px] font-mono">{src}</span>
                      <span className="text-emerald-400 font-mono font-bold">
                        {(score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full"
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
