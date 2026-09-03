"use client";

import React, { useState } from "react";
import { Layers, Activity, Search, Sparkles, Filter, ChevronRight, BarChart3, Database } from "lucide-react";
import { ScoredChunk, QueryConfig } from "../../types";
import { api } from "../../services/api";

export const RetrievalInspector: React.FC = () => {
  const [query, setQuery] = useState("quantum superposition gradient descent");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScoredChunk[]>([]);
  const [selectedResult, setSelectedResult] = useState<ScoredChunk | null>(null);

  const [config, setConfig] = useState<QueryConfig>({
    use_dense: true,
    use_sparse: true,
    use_reranker: true,
    dense_weight: 0.6,
    sparse_weight: 0.4,
    top_k: 10,
    rerank_top_k: 6,
  });

  const handleDiagnose = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await api.searchRetrieval(query, config);
      setResults(data);
      if (data.length > 0) {
        setSelectedResult(data[0]);
      } else {
        setSelectedResult(null);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Search Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Retrieval Stage Diagnostic Engine
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Inspect multi-stage fusion transparency: Dense Vector Cosine Similarity vs BM25 Lexical Score vs Reciprocal Rank Fusion vs Cross-Encoder Neural Reranking.
            </p>
          </div>
        </div>

        {/* Query Input */}
        <form onSubmit={handleDiagnose} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search query to inspect retrieval scores..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
          >
            <Activity className="w-4 h-4" />
            {loading ? "Diagnosing..." : "Run Diagnostics"}
          </button>
        </form>

        {/* Weights & Tuners */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-3 border-t border-slate-850 text-xs text-slate-300">
          <div className="space-y-1">
            <div className="flex justify-between text-[11px] text-slate-400">
              <span>Dense Weight (Vector)</span>
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
                  sparse_weight: Math.round((1 - parseFloat(e.target.value)) * 100) / 100,
                })
              }
              className="w-full accent-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-[11px] text-slate-400">
              <span>Sparse Weight (BM25)</span>
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
                  dense_weight: Math.round((1 - parseFloat(e.target.value)) * 100) / 100,
                })
              }
              className="w-full accent-cyan-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="diag-reranker"
              checked={config.use_reranker}
              onChange={(e) => setConfig({ ...config, use_reranker: e.target.checked })}
              className="rounded accent-indigo-600"
            />
            <label htmlFor="diag-reranker" className="text-xs cursor-pointer">
              Cross-Encoder Neural Reranking
            </label>
          </div>

          <div className="flex items-center justify-end text-[11px] text-slate-400">
            <span>RRF Constant: <strong className="text-slate-200">k=60</strong></span>
          </div>
        </div>
      </div>

      {/* Results Breakdown */}
      {results.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Candidates List */}
          <div className="lg:col-span-5 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Retrieved Ranked Candidates ({results.length})
            </h3>
            <div className="space-y-2">
              {results.map((res, idx) => {
                const isSelected = selectedResult?.chunk.id === res.chunk.id;
                return (
                  <div
                    key={res.chunk.id}
                    onClick={() => setSelectedResult(res)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? "bg-slate-900 border-indigo-500 shadow-md shadow-indigo-500/10"
                        : "glass-panel hover:bg-slate-900/60 border-slate-800"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs pb-1.5 border-b border-slate-800/80">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-400 font-mono">#{idx + 1}</span>
                        <span className="font-medium text-slate-200 truncate max-w-[160px]">
                          {res.chunk.metadata?.filename || "Document"}
                        </span>
                      </div>
                      <span className="font-mono text-xs font-bold text-emerald-400">
                        Score: {res.final_score.toFixed(4)}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 line-clamp-2 mt-2 font-mono">
                      {res.chunk.content}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Candidate Detailed Metrics */}
          {selectedResult && (
            <div className="lg:col-span-7 space-y-4">
              <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-cyan-400" />
                      Multimodal Score Distribution Matrix
                    </h4>
                    <p className="text-[11px] text-slate-400">
                      Document: <strong className="text-slate-200">{selectedResult.chunk.metadata?.filename || "Document"}</strong> (Chunk Index: #{selectedResult.chunk.chunk_index})
                    </p>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono font-bold">
                    Composite: {selectedResult.final_score.toFixed(4)}
                  </span>
                </div>

                {/* Score Breakdown Bars */}
                <div className="space-y-3">
                  {/* Dense */}
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-indigo-400 font-medium flex items-center gap-1.5">
                        <Database className="w-3.5 h-3.5" /> Dense Vector Search (Cosine)
                      </span>
                      <span className="font-mono text-slate-300">
                        Score: {selectedResult.dense_score !== undefined ? selectedResult.dense_score.toFixed(4) : "N/A"} (Rank: {selectedResult.dense_rank || "N/A"})
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(100, Math.max(0, (selectedResult.dense_score || 0) * 100))}%` }}
                      />
                    </div>
                  </div>

                  {/* Sparse BM25 */}
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-cyan-400 font-medium flex items-center gap-1.5">
                        <Search className="w-3.5 h-3.5" /> Sparse BM25 Keyword Search
                      </span>
                      <span className="font-mono text-slate-300">
                        Score: {selectedResult.sparse_score !== undefined ? selectedResult.sparse_score.toFixed(4) : "N/A"} (Rank: {selectedResult.sparse_rank || "N/A"})
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-cyan-400 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(100, Math.max(0, (selectedResult.sparse_score || 0) * 100))}%` }}
                      />
                    </div>
                  </div>

                  {/* RRF Score */}
                  {selectedResult.rrf_score !== undefined && (
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-purple-400 font-medium flex items-center gap-1.5">
                          <Layers className="w-3.5 h-3.5" /> Reciprocal Rank Fusion (RRF)
                        </span>
                        <span className="font-mono text-slate-300">
                          Score: {selectedResult.rrf_score.toFixed(4)}
                        </span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-purple-500 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, (selectedResult.rrf_score / 0.05) * 100)}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Neural Reranker */}
                  {selectedResult.rerank_score !== undefined && (
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-amber-400 font-medium flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5" /> Cross-Encoder Neural Reranking
                        </span>
                        <span className="font-mono text-slate-300">
                          Score: {selectedResult.rerank_score.toFixed(4)}
                        </span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-amber-400 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, Math.max(0, selectedResult.rerank_score * 100))}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Raw Passage Span Content */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-slate-400 font-medium">
                    <span>Passage Content & Span Bounds:</span>
                    <span className="font-mono text-[11px]">
                      Chars: [
                      {selectedResult.chunk.start_char ?? selectedResult.chunk.span?.start_char ?? 0}..
                      {selectedResult.chunk.end_char ?? selectedResult.chunk.span?.end_char ?? selectedResult.chunk.content.length}
                      ]
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 leading-relaxed max-h-56 overflow-y-auto whitespace-pre-wrap">
                    {selectedResult.chunk.content}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
