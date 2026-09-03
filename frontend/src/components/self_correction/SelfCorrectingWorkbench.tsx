"use client";

import React, { useState } from "react";
import {
  Sparkles,
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  FileText,
  Search,
  Zap,
  SlidersHorizontal,
  Layers,
  HelpCircle,
  Clock,
  ChevronRight,
  Database,
  Award
} from "lucide-react";
import {
  SelfCorrectingRAGResult,
  SelfCorrectionIteration,
  VerifiedClaimItem,
  DocumentInfo
} from "../../types";
import { api } from "../../services/api";

interface SelfCorrectingWorkbenchProps {
  documents?: DocumentInfo[];
}

export const SelfCorrectingWorkbench: React.FC<SelfCorrectingWorkbenchProps> = ({ documents = [] }) => {
  const [query, setQuery] = useState("Explain the multi-head self-attention mechanism and parameter efficiency in Transformer architectures.");
  const [maxIterations, setMaxIterations] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SelfCorrectingRAGResult | null>(null);
  const [selectedIteration, setSelectedIteration] = useState<SelfCorrectionIteration | null>(null);

  const presetQueries = [
    {
      title: "Multi-Topic Technical Query (Requires Recovery)",
      q: "Explain quantum annealing and cryogenic thermal thresholds in supercomputing architectures.",
    },
    {
      title: "Contradiction Disambiguation",
      q: "What is the accuracy of Transformer models across different benchmark datasets?",
    },
    {
      title: "Standard Grounded Query (First-Pass)",
      q: "How does Reciprocal Rank Fusion (RRF) balance dense vectors and sparse BM25?",
    },
  ];

  const handleExecute = async (overrideQuery?: string) => {
    const q = overrideQuery || query;
    if (!q.trim()) return;

    try {
      setLoading(true);
      const res = await api.executeSelfCorrection(q, {
        max_iterations: maxIterations,
        top_k: 8,
      });
      setResult(res);
      if (res.iterations_trace.length > 0) {
        setSelectedIteration(res.iterations_trace[res.iterations_trace.length - 1]);
      }
    } catch (err) {
      console.error("Self-correcting execution failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "recovered":
        return (
          <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> Self-Corrected & Recovered
          </span>
        );
      case "first_pass_success":
        return (
          <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> First-Pass Sufficient
          </span>
        );
      case "abstained":
        return (
          <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-bold flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Abstained (Insufficient Evidence)
          </span>
        );
      default:
        return (
          <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-400 text-xs font-bold">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden shadow-xl shadow-amber-950/20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-amber-600/10 via-orange-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/25">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  Self-Correcting Retrieval Engine
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    Phase 7 Active
                  </span>
                </h2>
                <p className="text-xs text-slate-400">
                  Iterative retrieval with quality evaluation, targeted query rewriting, cross-iteration evidence accumulation, and claim verification.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Config Badges */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <RefreshCw className="w-4 h-4 text-amber-400" />
              <span className="text-slate-400">Max Iterations:</span>
              <span className="font-mono text-amber-300 font-bold">{maxIterations} Attempts</span>
            </div>

            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-400">Zero-Hallucination:</span>
              <span className="font-mono text-emerald-300 font-medium">Claim Verification & Filtering</span>
            </div>
          </div>
        </div>

        {/* Query Input & Actions */}
        <div className="flex flex-col sm:flex-row gap-3 mt-6 pt-5 border-t border-slate-800/80">
          <input
            type="text"
            placeholder="Ask a complex query requiring multi-iteration retrieval or contradiction disambiguation..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500 font-sans"
            onKeyDown={(e) => e.key === "Enter" && handleExecute()}
          />
          <button
            onClick={() => handleExecute()}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold text-xs shadow-lg shadow-amber-600/25 transition-all disabled:opacity-50 shrink-0 flex items-center justify-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Running Self-Correction..." : "Execute Self-Correction"}
          </button>
        </div>

        {/* Preset Badges */}
        <div className="flex flex-wrap items-center gap-2 mt-3 text-xs">
          <span className="text-slate-500 font-mono text-[11px]">Presets:</span>
          {presetQueries.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(p.q);
                handleExecute(p.q);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:border-amber-500/50 transition-all text-[11px]"
            >
              {p.title}
            </button>
          ))}
        </div>
      </div>

      {/* Main Results Workspace */}
      {result && (
        <div className="space-y-6">
          {/* Top Observability Metrics Dashboard */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Loop Status</div>
              <div className="pt-1">{getStatusBadge(result.status)}</div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Total Iterations</div>
              <div className="text-xl font-bold font-mono text-amber-400">
                {result.total_iterations} <span className="text-xs text-slate-500 font-normal">/ {result.max_iterations_allowed} max</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Evidence Coverage</div>
              <div className="text-xl font-bold font-mono text-emerald-400">
                {result.final_evidence_coverage}%
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Accumulated Chunks</div>
              <div className="text-xl font-bold font-mono text-cyan-400">
                {result.accumulated_chunks.length} <span className="text-xs text-slate-500 font-normal">unique</span>
              </div>
            </div>
          </div>

          {/* Iteration Stepper & Timeline */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              Self-Correction Retrieval Timeline ({result.iterations_trace.length} Attempts)
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.iterations_trace.map((it) => {
                const isSelected = selectedIteration?.iteration_number === it.iteration_number;
                const isSuccess = it.decision_taken === "generate";
                return (
                  <div
                    key={it.iteration_number}
                    onClick={() => setSelectedIteration(it)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all space-y-3 ${
                      isSelected
                        ? "bg-amber-950/30 border-amber-500/60 shadow-lg shadow-amber-500/10"
                        : "bg-slate-950/60 border-slate-800 hover:bg-slate-900 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
                        Attempt {it.iteration_number}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                        isSuccess ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"
                      }`}>
                        {it.decision_taken}
                      </span>
                    </div>

                    <div className="text-xs text-slate-200 font-mono bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 truncate">
                      "{it.search_query}"
                    </div>

                    <div className="text-[11px] text-slate-400 space-y-1 font-mono">
                      <div className="flex justify-between">
                        <span>Strategy:</span>
                        <span className="text-slate-300">{it.rewrite_strategy || "Initial Original"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Retrieved:</span>
                        <span className="text-slate-300">+{it.retrieved_chunks_count} chunks</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Quality Score:</span>
                        <span className="text-amber-300 font-bold">
                          {it.quality_evaluation?.overall_quality.toFixed(2) || "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Answer Synthesis & Verification Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Final Verified Answer (7 cols) */}
            <div className="lg:col-span-7 space-y-5">
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4" />
                    Verified Answer Synthesis
                  </span>
                  {result.verification?.was_regenerated && (
                    <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-mono">
                      Filtered Unsupported Claims
                    </span>
                  )}
                </div>

                <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed space-y-3">
                  {result.final_answer_markdown}
                </div>
              </div>
            </div>

            {/* Right: Claim Verification Inspector (5 cols) */}
            <div className="lg:col-span-5 space-y-5">
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Award className="w-4 h-4 text-indigo-400" />
                    Claim Verification Inspector
                  </h4>
                  <span className="text-[10px] font-mono text-slate-400">
                    {result.verification?.supported_claims_count || 0} Supported / {result.verification?.extracted_claims.length || 0} Claims
                  </span>
                </div>

                <div className="space-y-2.5 max-h-[460px] overflow-y-auto pr-1">
                  {result.verification?.verified_claim_items.map((item, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl border text-xs space-y-2 ${
                        item.status === "supported"
                          ? "bg-slate-950 border-emerald-900/40"
                          : item.status === "contradicted"
                          ? "bg-rose-950/20 border-rose-900/40"
                          : "bg-slate-950 border-slate-800"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-medium text-slate-200">{item.claim_text}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold shrink-0 ${
                          item.status === "supported"
                            ? "bg-emerald-500/20 text-emerald-400"
                            : item.status === "contradicted"
                            ? "bg-rose-500/20 text-rose-400"
                            : "bg-slate-800 text-slate-400"
                        }`}>
                          {item.status}
                        </span>
                      </div>

                      {item.supporting_citations.length > 0 && (
                        <div className="text-[10px] text-slate-400 bg-slate-900/80 p-2 rounded border border-slate-800/80 italic">
                          "{item.supporting_citations[0].exact_quote}"
                          <div className="text-[9px] text-emerald-400 font-mono mt-0.5 not-italic">
                            Source: {item.supporting_citations[0].document_filename} (P.{item.supporting_citations[0].page_number})
                          </div>
                        </div>
                      )}

                      {item.verification_note && (
                        <div className="text-[10px] text-slate-500 font-mono">
                          {item.verification_note}
                        </div>
                      )}
                    </div>
                  ))}

                  {(!result.verification || result.verification.verified_claim_items.length === 0) && (
                    <div className="text-xs text-slate-500 italic p-4 text-center">
                      No claims extracted for verification.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
