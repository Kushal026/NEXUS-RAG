"use client";

import React, { useState } from "react";
import {
  GitCommit,
  GitBranch,
  ArrowDown,
  Layers,
  Search,
  Zap,
  CheckCircle2,
  Clock,
  Tag,
  AlertCircle,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  FileText,
  Activity
} from "lucide-react";
import { MultiHopReasoningTrace, StepEvidence, PlanStep } from "../../types";

interface ResearchReasoningTimelineProps {
  trace: MultiHopReasoningTrace;
}

export const ResearchReasoningTimeline: React.FC<ResearchReasoningTimelineProps> = ({ trace }) => {
  const [expandedStep, setExpandedStep] = useState<number | null>(1);

  const toggleStep = (stepNum: number) => {
    setExpandedStep(expandedStep === stepNum ? null : stepNum);
  };

  const plan = trace.plan;
  const steps = trace.step_evidences;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-indigo-500/40 space-y-6">
      {/* Timeline Plan Overview Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-indigo-400" />
            <h3 className="text-sm font-bold text-white">
              Research Reasoning & Multi-Hop Retrieval Timeline
            </h3>
            <span className="text-[10px] uppercase font-mono px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {plan.query_category.replace(/_/g, " ")}
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-3xl">
            {plan.reasoning_summary}
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>{trace.total_hops_executed} / {plan.estimated_hops} Hops</span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{trace.total_reasoning_time_ms} ms</span>
          </div>
        </div>
      </div>

      {/* Sequential Multi-Hop Timeline Path */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-indigo-500 before:via-cyan-500 before:to-emerald-500">
        {steps.map((step, idx) => {
          const isExpanded = expandedStep === step.step_number;
          const isLast = idx === steps.length - 1;

          return (
            <div key={step.step_number} className="relative space-y-2">
              {/* Step Node Marker */}
              <div
                className={`absolute -left-[30px] top-1.5 w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold font-mono transition-all ${
                  isExpanded
                    ? "bg-indigo-600 border-indigo-300 text-white shadow-lg shadow-indigo-500/50"
                    : "bg-slate-900 border-slate-700 text-slate-400"
                }`}
              >
                {step.step_number}
              </div>

              {/* Step Card Container */}
              <div className="rounded-xl border border-slate-800 bg-slate-950/80 overflow-hidden transition-all hover:border-slate-700">
                <button
                  onClick={() => toggleStep(step.step_number)}
                  className="w-full p-4 text-left flex items-center justify-between gap-4 hover:bg-slate-900/40 transition-all"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-bold text-slate-200">
                        Hop {step.step_number}: {step.sub_query}
                      </span>
                      {step.was_rewritten && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 flex items-center gap-1 font-mono">
                          <RefreshCw className="w-3 h-3" /> Query Rewritten
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0 text-xs">
                    <div className="hidden sm:flex items-center gap-1.5 text-slate-400 font-mono text-[11px]">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {step.execution_time_ms} ms
                    </div>
                    <div className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono text-[11px] font-bold">
                      {(step.confidence_score * 100).toFixed(0)}% Conf
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </button>

                {/* Expanded Step Evidence Drawer */}
                {isExpanded && (
                  <div className="p-4 pt-2 border-t border-slate-850 space-y-4 text-xs">
                    {/* Rewritten query note if applicable */}
                    {step.was_rewritten && step.original_sub_query && (
                      <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 flex items-start gap-2 text-[11px]">
                        <RefreshCw className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        <div>
                          <strong>Low-Confidence Query Reformulation:</strong> Expanded initial sub-query{" "}
                          <span className="font-mono text-amber-200">"{step.original_sub_query}"</span> with synonym broadening to maximize recall.
                        </div>
                      </div>
                    )}

                    {/* Extracted Intermediate Facts */}
                    {step.extracted_facts.length > 0 && (
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Discovered Intermediate Evidence & Facts
                        </span>
                        <div className="space-y-1">
                          {step.extracted_facts.map((fact, fIdx) => (
                            <div
                              key={fIdx}
                              className="p-2.5 rounded-lg bg-slate-900 border border-slate-850 text-slate-200 leading-relaxed font-sans"
                            >
                              {fact}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Discovered Entities & Part Numbers */}
                    {step.discovered_entities.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap pt-1">
                        <span className="text-[11px] text-slate-400 font-semibold flex items-center gap-1">
                          <Tag className="w-3 h-3 text-cyan-400" /> Discovered Entities:
                        </span>
                        {step.discovered_entities.map((ent, eIdx) => (
                          <span
                            key={eIdx}
                            className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono text-[10px]"
                          >
                            {ent}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Retrieved Passages (Top Evidence Chunks) */}
                    <div className="space-y-1.5 pt-1">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                        <FileText className="w-3 h-3 text-indigo-400" /> Retrieved Passages ({step.retrieved_chunks.length} chunks)
                      </span>
                      <div className="space-y-1.5">
                        {step.retrieved_chunks.slice(0, 3).map((sc, scIdx) => (
                          <div
                            key={sc.chunk.id}
                            className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800 flex items-start justify-between gap-3"
                          >
                            <div className="min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-indigo-400 font-bold">#{scIdx + 1}</span>
                                <span className="font-semibold text-slate-300 truncate">
                                  {sc.chunk.metadata?.filename || "Document"}
                                </span>
                                {(sc.chunk.page_number || sc.chunk.span?.page_number) && (
                                  <span className="text-[10px] text-cyan-400 font-mono">
                                    Page {sc.chunk.page_number || sc.chunk.span?.page_number}
                                  </span>
                                )}
                              </div>
                              <p className="text-[11px] text-slate-400 font-mono mt-1 line-clamp-2">
                                {sc.chunk.content}
                              </p>
                            </div>
                            <span className="font-mono text-[11px] text-emerald-400 font-bold shrink-0">
                              Score: {sc.final_score.toFixed(4)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Final Unified Synthesis Node */}
        <div className="relative pt-2">
          <div className="absolute -left-[30px] top-4 w-6 h-6 rounded-full bg-emerald-600 border-2 border-emerald-300 text-white flex items-center justify-center text-[10px] font-bold shadow-lg shadow-emerald-500/50">
            ✓
          </div>
          <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-300 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="font-semibold">
                Reasoning Completed ({trace.stop_reason.replace(/_/g, " ")}) — Synthesizing Cross-Hop Claims
              </span>
            </div>
            <span className="font-mono text-[11px] text-slate-400">
              {trace.all_accumulated_chunks.length} Evidence Chunks Unified
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
