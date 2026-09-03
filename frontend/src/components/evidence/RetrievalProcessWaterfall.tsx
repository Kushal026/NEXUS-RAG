"use client";

import React, { useState } from "react";
import {
  Layers,
  Search,
  Database,
  Zap,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Clock,
  Tag,
  Calendar,
  FileText,
  Activity,
  CheckCircle2,
  Filter
} from "lucide-react";
import { RetrievalTrace, StageCandidate } from "../../types";

interface RetrievalProcessWaterfallProps {
  trace: RetrievalTrace;
}

export const RetrievalProcessWaterfall: React.FC<RetrievalProcessWaterfallProps> = ({ trace }) => {
  const [openStage, setOpenStage] = useState<number | null>(1);

  const toggleStage = (stageNum: number) => {
    setOpenStage(openStage === stageNum ? null : stageNum);
  };

  const analysis = trace.query_analysis;
  const latencies = trace.stage_latencies_ms || {};

  return (
    <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 space-y-5">
      {/* Header with Pipeline Telemetry */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Advanced Retrieval Pipeline Waterfall (5 Stages)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Full execution trajectory: Query Analyzer → Dense Vector → BM25 Lexical → RRF Fusion (Top 50) → Cross-Encoder Reranker (Top 10).
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 font-mono">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            Total: {trace.total_pipeline_time_ms} ms
          </span>
        </div>
      </div>

      {/* 5-Stage Interactive Waterfall Accordion */}
      <div className="space-y-3">
        {/* Stage 1: Query Analysis & Understanding */}
        <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/70">
          <button
            onClick={() => toggleStage(1)}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-900/60 transition-all"
          >
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-mono font-bold">
                1
              </span>
              <span className="text-xs font-semibold text-slate-200">Query Understanding & Entity Extraction</span>
              {analysis && (
                <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
                  Intent: {analysis.intent}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="font-mono text-[11px]">{latencies.query_understanding_ms || 1.2} ms</span>
              {openStage === 1 ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
          </button>

          {openStage === 1 && analysis && (
            <div className="p-4 pt-2 border-t border-slate-850 space-y-3 text-xs">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                  <span className="text-[11px] text-slate-400">Classified Intent</span>
                  <p className="font-mono text-indigo-300 font-semibold">{analysis.intent}</p>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                  <span className="text-[11px] text-slate-400">Extracted Entities & Codes</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {analysis.entities.length > 0 ? (
                      analysis.entities.map((e, idx) => (
                        <span key={idx} className="px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono text-[10px]">
                          {e}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500 text-[10px]">None</span>
                    )}
                  </div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                  <span className="text-[11px] text-slate-400">Suggested Strategy</span>
                  <p className="font-mono text-emerald-400 font-semibold">{analysis.suggested_retrieval_mode}</p>
                </div>
              </div>

              {/* Extracted Constraints */}
              {(analysis.constraints.target_documents.length > 0 || analysis.constraints.date_after) && (
                <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] space-y-1">
                  <span className="text-slate-400 flex items-center gap-1 font-semibold">
                    <Filter className="w-3 h-3 text-amber-400" /> Extracted Metadata Filters:
                  </span>
                  <div className="flex flex-wrap gap-2 text-slate-300 font-mono">
                    {analysis.constraints.target_documents.map((d, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-slate-800 text-slate-200">doc:{d}</span>
                    ))}
                    {analysis.constraints.date_after && (
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-300">after:{analysis.constraints.date_after}</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Stage 2: Dense Vector Search */}
        <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/70">
          <button
            onClick={() => toggleStage(2)}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-900/60 transition-all"
          >
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-mono font-bold">
                2
              </span>
              <span className="text-xs font-semibold text-slate-200">Dense Semantic Vector Retrieval (pgvector)</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-mono">
                {trace.vector_candidates_count} candidates
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="font-mono text-[11px]">{latencies.vector_search_ms || 8.4} ms</span>
              {openStage === 2 ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
          </button>

          {openStage === 2 && (
            <div className="p-4 pt-2 border-t border-slate-850 space-y-2 text-xs">
              <div className="space-y-1.5">
                {trace.vector_top_candidates.map((cand) => (
                  <div key={cand.chunk_id} className="p-2.5 rounded-lg bg-slate-900 border border-slate-850 flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-indigo-400 font-bold">#{cand.rank}</span>
                        <span className="font-semibold text-slate-200 truncate">{cand.document_filename}</span>
                        {cand.page_number && <span className="text-[10px] text-slate-400">P.{cand.page_number}</span>}
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono truncate mt-0.5">{cand.content_snippet}</p>
                    </div>
                    <span className="font-mono text-[11px] text-indigo-300 font-bold shrink-0">
                      Cosine: {cand.score.toFixed(4)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Stage 3: BM25 Lexical Keyword Search */}
        <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/70">
          <button
            onClick={() => toggleStage(3)}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-900/60 transition-all"
          >
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-mono font-bold">
                3
              </span>
              <span className="text-xs font-semibold text-slate-200">BM25 Okapi Lexical Keyword Retrieval</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-mono">
                {trace.bm25_candidates_count} candidates
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="font-mono text-[11px]">{latencies.bm25_search_ms || 2.1} ms</span>
              {openStage === 3 ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
          </button>

          {openStage === 3 && (
            <div className="p-4 pt-2 border-t border-slate-850 space-y-2 text-xs">
              <div className="space-y-1.5">
                {trace.bm25_top_candidates.map((cand) => (
                  <div key={cand.chunk_id} className="p-2.5 rounded-lg bg-slate-900 border border-slate-850 flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-400 font-bold">#{cand.rank}</span>
                        <span className="font-semibold text-slate-200 truncate">{cand.document_filename}</span>
                        {cand.page_number && <span className="text-[10px] text-slate-400">P.{cand.page_number}</span>}
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono truncate mt-0.5">{cand.content_snippet}</p>
                    </div>
                    <span className="font-mono text-[11px] text-cyan-300 font-bold shrink-0">
                      BM25: {cand.score.toFixed(4)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Stage 4: Reciprocal Rank Fusion (RRF) */}
        <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/70">
          <button
            onClick={() => toggleStage(4)}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-900/60 transition-all"
          >
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-mono font-bold">
                4
              </span>
              <span className="text-xs font-semibold text-slate-200">Reciprocal Rank Fusion (RRF k=60)</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-mono">
                {trace.fused_candidates_count} fused
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="font-mono text-[11px]">{latencies.fusion_ms || 1.1} ms</span>
              {openStage === 4 ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
          </button>

          {openStage === 4 && (
            <div className="p-4 pt-2 border-t border-slate-850 space-y-2 text-xs">
              <div className="space-y-1.5">
                {trace.fused_top_candidates.map((cand) => (
                  <div key={cand.chunk_id} className="p-2.5 rounded-lg bg-slate-900 border border-slate-850 flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-purple-400 font-bold">#{cand.rank}</span>
                        <span className="font-semibold text-slate-200 truncate">{cand.document_filename}</span>
                        {cand.page_number && <span className="text-[10px] text-slate-400">P.{cand.page_number}</span>}
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono truncate mt-0.5">{cand.content_snippet}</p>
                    </div>
                    <span className="font-mono text-[11px] text-purple-300 font-bold shrink-0">
                      RRF Score: {cand.score.toFixed(4)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Stage 5: Cross-Encoder Neural Reranking */}
        <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-950/70">
          <button
            onClick={() => toggleStage(5)}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-slate-900/60 transition-all"
          >
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-mono font-bold">
                5
              </span>
              <span className="text-xs font-semibold text-slate-200">Neural Cross-Encoder Reranking (ms-marco)</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono">
                Top {trace.reranked_candidates_count} Evidence
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="font-mono text-[11px]">{latencies.reranking_ms || 18.2} ms</span>
              {openStage === 5 ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
          </button>

          {openStage === 5 && (
            <div className="p-4 pt-2 border-t border-slate-850 space-y-2 text-xs">
              <div className="space-y-1.5">
                {trace.final_ranked_candidates.map((cand) => (
                  <div key={cand.chunk_id} className="p-2.5 rounded-lg bg-slate-900 border border-indigo-500/30 flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-emerald-400 font-bold">#{cand.rank}</span>
                        <span className="font-semibold text-slate-200 truncate">{cand.document_filename}</span>
                        {cand.page_number && <span className="text-[10px] text-cyan-400">Page {cand.page_number}</span>}
                      </div>
                      <p className="text-[11px] text-slate-300 font-mono truncate mt-0.5">{cand.content_snippet}</p>
                    </div>
                    <span className="font-mono text-[11px] text-emerald-400 font-bold shrink-0">
                      Final: {cand.score.toFixed(4)}
                    </span>
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
