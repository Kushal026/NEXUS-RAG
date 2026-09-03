"use client";

import React, { useState } from "react";
import {
  Zap,
  Sparkles,
  Bot,
  Layers,
  Search,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  ChevronRight,
  Sliders,
  FileText,
  Share2,
  Table as TableIcon,
  ShieldAlert,
  ArrowRight,
  Database,
  BarChart2,
  Copy,
  Check
} from "lucide-react";
import { api } from "@/services/api";
import {
  ResearchAgentReportResult,
  DocumentInfo
} from "@/types";

interface ResearchAgentWorkbenchProps {
  documents: DocumentInfo[];
}

export const ResearchAgentWorkbench: React.FC<ResearchAgentWorkbenchProps> = ({ documents }) => {
  const [goal, setGoal] = useState("");
  const [maxIterations, setMaxIterations] = useState(3);
  const [maxSearches, setMaxSearches] = useState(8);
  const [maxTime, setMaxTime] = useState(30);
  const [enableGraph, setEnableGraph] = useState(true);
  const [enableContradiction, setEnableContradiction] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResearchAgentReportResult | null>(null);
  const [copied, setCopied] = useState(false);

  const presets = [
    "Analyze current approaches to detecting deepfakes and compare their performance.",
    "Investigate Transformer multi-head attention optimization across hardware architectures.",
    "Evaluate cryogenic thermal thresholds and error rates in supercomputing systems.",
    "Assess hallucination mitigation techniques and factual NLI verification in RAG pipelines."
  ];

  const handleExecuteResearch = async (overrideGoal?: string) => {
    const targetGoal = overrideGoal !== undefined ? overrideGoal : goal;
    if (!targetGoal.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await api.executeResearchAgent({
        goal: targetGoal,
        max_iterations: maxIterations,
        max_searches: maxSearches,
        max_time_seconds: maxTime,
        enable_graph_traversal: enableGraph,
        enable_contradiction_detection: enableContradiction
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute research agent");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyReport = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.report_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getActionTypeBadge = (type: string) => {
    switch (type) {
      case "planning":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">PLANNING</span>;
      case "graph_traversal":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">GRAPH TRAVERSAL</span>;
      case "hybrid_search":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-violet-500/10 text-violet-400 border border-violet-500/20">HYBRID SEARCH</span>;
      case "evidence_analysis":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">EVIDENCE NLI</span>;
      case "gap_detection":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">GAP DETECTION</span>;
      case "synthesis":
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">REPORT SYNTHESIS</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20">{type.toUpperCase()}</span>;
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-rose-950/50 via-pink-950/30 to-slate-900/40 border border-rose-800/40 p-6 backdrop-blur-xl shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase tracking-wide flex items-center gap-1">
                <Zap className="w-3 h-3 text-rose-400" />
                Phase 9 Autonomous Agent
              </span>
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Orchestrating RAG, Graph & Evidence Engines
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Bot className="w-7 h-7 text-rose-400" />
              NEXUS Research Agent
            </h2>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Autonomous, bounded research orchestrator that plans, retrieves, reads evidence, detects gaps, checks contradictions, and compiles comprehensive academic research reports.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <div className="text-right">
              <p className="text-[11px] text-slate-400">Target Knowledge Vault</p>
              <p className="text-xs font-semibold text-rose-300">{documents.length} Documents Indexed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Goal Input & Controls */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4 backdrop-blur-md">
        <div className="flex flex-col gap-3">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5 text-rose-400" />
            Define Research Goal or Analytical Hypothesis:
          </label>
          <div className="flex flex-col md:flex-row gap-3">
            <input
              type="text"
              placeholder="e.g. Analyze current approaches to detecting deepfakes and compare their performance..."
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleExecuteResearch()}
              className="flex-1 px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-rose-500/50 focus:border-rose-500 transition-all"
            />
            <button
              onClick={() => handleExecuteResearch()}
              disabled={loading || !goal.trim()}
              className="px-6 py-3 bg-gradient-to-r from-rose-600 via-pink-600 to-red-600 hover:from-rose-500 hover:to-red-500 disabled:opacity-50 text-white rounded-xl text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-rose-600/20 transition-all cursor-pointer"
            >
              {loading ? (
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Execute Research
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-medium text-slate-500">Suggested Research Goals:</span>
          <div className="flex items-center gap-2 flex-wrap">
            {presets.map((p, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setGoal(p);
                  handleExecuteResearch(p);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-rose-500/40 text-slate-300 text-[11px] transition-all text-left"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Configurable Budget Controls */}
        <div className="border-t border-slate-800/80 pt-3 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-6 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Max Iterations:</span>
              <select
                value={maxIterations}
                onChange={(e) => setMaxIterations(Number(e.target.value))}
                className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200"
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n} Iteration{n > 1 ? "s" : ""}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-slate-400">Max Searches:</span>
              <select
                value={maxSearches}
                onChange={(e) => setMaxSearches(Number(e.target.value))}
                className="bg-slate-950 border border-slate-800 rounded px-2 py-1 text-slate-200"
              >
                {[4, 6, 8, 10, 12].map((n) => (
                  <option key={n} value={n}>{n} Searches</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-slate-400">Timeout:</span>
              <span className="text-slate-200 font-mono">{maxTime}s</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={enableGraph}
                onChange={(e) => setEnableGraph(e.target.checked)}
                className="rounded border-slate-800 text-rose-600 focus:ring-rose-500"
              />
              <span className="text-xs">Graph Traversal</span>
            </label>

            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={enableContradiction}
                onChange={(e) => setEnableContradiction(e.target.checked)}
                className="rounded border-slate-800 text-rose-600 focus:ring-rose-500"
              />
              <span className="text-xs">NLI Contradiction Check</span>
            </label>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Results Workspace */}
      {result && (
        <div className="space-y-6">
          {/* Budget Telemetry Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Estimated Tokens</p>
              <p className="text-lg font-bold text-white mt-0.5 font-mono">{result.telemetry.total_tokens_estimated.toLocaleString()}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Search className="w-3 h-3 text-rose-400" /> Searches
              </p>
              <p className="text-lg font-bold text-rose-300 mt-0.5">{result.telemetry.searches_executed}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Share2 className="w-3 h-3 text-cyan-400" /> Graph Queries
              </p>
              <p className="text-lg font-bold text-cyan-300 mt-0.5">{result.telemetry.graph_queries_executed}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Clock className="w-3 h-3 text-amber-400" /> Time Elapsed
              </p>
              <p className="text-lg font-bold text-amber-300 mt-0.5">{result.telemetry.execution_time_seconds}s</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-400" /> Confidence
              </p>
              <p className="text-lg font-bold text-emerald-300 mt-0.5">{Math.round(result.confidence_score * 100)}%</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Termination</p>
              <p className="text-xs font-semibold text-slate-200 mt-1 uppercase font-mono">
                {result.telemetry.termination_reason.replace("_", " ")}
              </p>
            </div>
          </div>

          {/* Research Plan & Action Trace */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Research Plan Sub-Questions */}
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-5 space-y-4 backdrop-blur-md">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-rose-400" />
                  Research Plan ({result.plan.sub_questions.length} Sub-Questions)
                </h3>
              </div>

              <div className="space-y-3">
                {result.plan.sub_questions.map((sq, i) => (
                  <div
                    key={sq.id}
                    className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-slate-200">Sub-Question {i + 1}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        sq.status === "answered"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}>
                        {sq.status === "answered" ? "✅ Answered" : "⚠️ Partial Gap"}
                      </span>
                    </div>
                    <p className="text-slate-300 font-medium">{sq.question}</p>
                    {sq.key_findings_summary && (
                      <p className="text-[11px] text-slate-400 bg-slate-900/80 p-2 rounded border border-slate-800/60">
                        {sq.key_findings_summary}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Right: High-Level Action Trace */}
            <div className="lg:col-span-2 rounded-2xl bg-slate-900/60 border border-slate-800/80 p-5 space-y-4 backdrop-blur-md">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Zap className="w-4 h-4 text-rose-400" />
                  High-Level Research Action Trace ({result.action_trace.length} Steps)
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">No Hidden CoT Exposed</span>
              </div>

              <div className="space-y-2.5">
                {result.action_trace.map((step) => (
                  <div
                    key={step.step_number}
                    className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start gap-3 text-xs"
                  >
                    <div className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                      {step.step_number}
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        {getActionTypeBadge(step.action_type)}
                        <span className="text-[10px] font-mono text-slate-500">{step.timestamp_ms}ms</span>
                      </div>
                      <p className="text-slate-200">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Generated 9-Section Academic Report */}
          <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 space-y-5 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-rose-400" />
                Synthesized Academic Research Report
              </h3>
              <button
                onClick={handleCopyReport}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-medium flex items-center gap-1.5 transition-all"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? "Copied!" : "Copy Report Markdown"}
              </button>
            </div>

            <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed bg-slate-950/80 p-6 rounded-xl border border-slate-800 whitespace-pre-wrap font-sans">
              {result.report_markdown}
            </div>
          </div>

          {/* Structured Source & Evidence Table */}
          <div className="rounded-2xl bg-slate-900/60 border border-slate-800/80 p-6 space-y-4 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <TableIcon className="w-5 h-5 text-emerald-400" />
                Source & Evidence Provenance Table ({result.source_table.length} Sources)
              </h3>
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
              <table className="w-full text-xs text-left text-slate-300">
                <thead className="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Source Document</th>
                    <th className="px-4 py-3 font-semibold">Modality / Type</th>
                    <th className="px-4 py-3 font-semibold">Date</th>
                    <th className="px-4 py-3 font-semibold">Relevance</th>
                    <th className="px-4 py-3 font-semibold">Reliability</th>
                    <th className="px-4 py-3 font-semibold">Claims Used</th>
                    <th className="px-4 py-3 font-semibold">Provenance</th>
                  </tr>
                </thead>
                <tbody>
                  {result.source_table.map((row, idx) => (
                    <tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-900/40">
                      <td className="px-4 py-2.5 font-mono text-white font-medium">{row.source_filename}</td>
                      <td className="px-4 py-2.5 text-slate-400">{row.source_type}</td>
                      <td className="px-4 py-2.5 text-slate-400 font-mono">{row.publication_date}</td>
                      <td className="px-4 py-2.5 font-mono text-emerald-400">{row.relevance_score.toFixed(3)}</td>
                      <td className="px-4 py-2.5 font-mono text-cyan-400">{row.reliability_score.toFixed(3)}</td>
                      <td className="px-4 py-2.5 font-mono text-slate-300">{row.used_claims_count}</td>
                      <td className="px-4 py-2.5 text-slate-400 font-mono">Page {row.provenance_page || 1}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
