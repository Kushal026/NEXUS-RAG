"use client";

import React from "react";
import {
  ShieldCheck,
  FileText,
  Layers,
  Activity,
  Cpu,
  Database,
  Search,
  ArrowRight,
  Server,
  Zap,
  CheckCircle2,
  Sliders
} from "lucide-react";
import { SystemStatus, DocumentInfo } from "../../types";

interface DashboardOverviewProps {
  status: SystemStatus | null;
  documents: DocumentInfo[];
  onNavigate: (tab: "dashboard" | "documents" | "research" | "settings") => void;
  onSelectDocument: (doc: DocumentInfo) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  status,
  documents,
  onNavigate,
  onSelectDocument,
}) => {
  const totalChunks = documents.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
  const totalSize = documents.reduce((acc, d) => acc + (d.file_size || 0), 0);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Platform Banner */}
      <div className="relative overflow-hidden glass-panel-glow p-8 rounded-3xl border border-indigo-500/30">
        <div className="absolute -right-12 -top-12 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              NEXUS-RAG • Neural Evidence Intelligence Platform
            </div>
            <h2 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              Evidence-First Retrieval & Explainable Neural Synthesis
            </h2>
            <p className="text-xs lg:text-sm text-slate-300 leading-relaxed">
              Transform unstructured multi-format documents (PDF, DOCX, Markdown, TXT) into verified knowledge with dual-index semantic search (Dense Cosine Vectors + BM25 Okapi + Cross-Encoder Reranking) and claim-level source citations.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate("research")}
              className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
            >
              <Search className="w-4 h-4" />
              Start Research Query
            </button>
            <button
              onClick={() => onNavigate("documents")}
              className="px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-800 text-xs font-medium transition-all flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Manage Knowledge Vault
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Indexed Documents</span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">{documents.length}</span>
            <span className="text-[11px] text-slate-400">{(totalSize / 1024).toFixed(1)} KB Total</span>
          </div>
          <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-indigo-500 rounded-full w-full" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Semantic Chunks</span>
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">{totalChunks}</span>
            <span className="text-[11px] text-slate-400">Dense + BM25</span>
          </div>
          <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-cyan-400 rounded-full w-full" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Embedding Engine</span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-bold text-slate-100 font-mono truncate max-w-[150px]">
              {status?.embedding_provider || "all-MiniLM-L6-v2"}
            </span>
            <span className="text-[11px] text-emerald-400 font-semibold">384-dim</span>
          </div>
          <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-purple-500 rounded-full w-full" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Neural Reranker</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-bold text-slate-100 font-mono">Cross-Encoder</span>
            <span className="text-[11px] text-indigo-400 font-semibold">ms-marco</span>
          </div>
          <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-amber-400 rounded-full w-full" />
          </div>
        </div>
      </div>

      {/* Grid: Recent Knowledge Sources & Architectural Engine Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Ingested Documents */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Recent Knowledge Sources ({documents.length})
            </h3>
            <button
              onClick={() => onNavigate("documents")}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              View Vault <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {documents.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400 space-y-3">
              <p>No documents uploaded yet in the knowledge vault.</p>
              <button
                onClick={() => onNavigate("documents")}
                className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-medium text-xs shadow-md shadow-indigo-600/20"
              >
                Upload First Document
              </button>
            </div>
          ) : (
            <div className="space-y-2.5">
              {documents.slice(0, 5).map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => onSelectDocument(doc)}
                  className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-850 hover:border-indigo-500/40 cursor-pointer transition-all flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-indigo-400">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-semibold text-slate-200 truncate">{doc.filename}</h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        <span className="uppercase font-mono text-[10px] text-indigo-300">{doc.file_type}</span> • {(doc.file_size / 1024).toFixed(1)} KB • {doc.chunk_count} chunks
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-slate-400 hover:text-white flex items-center gap-1">
                    Details <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Engine Pipeline Diagnostics */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Engine Architecture Telemetry
            </h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Online
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Database Layer</span>
                <p className="text-[11px] text-slate-400">PostgreSQL + pgvector / Local Vector Store</p>
              </div>
              <span className="font-mono text-emerald-400 font-semibold">Active</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Retrieval Fusion</span>
                <p className="text-[11px] text-slate-400">Reciprocal Rank Fusion (k=60)</p>
              </div>
              <span className="font-mono text-indigo-400 font-semibold">RRF Enabled</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Evidence Citation Engine</span>
                <p className="text-[11px] text-slate-400">Claim Extraction & Span Attribution</p>
              </div>
              <span className="font-mono text-cyan-400 font-semibold">Verified</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-200">Streaming SSE Protocol</span>
                <p className="text-[11px] text-slate-400">Real-Time Token & Metadata Stream</p>
              </div>
              <span className="font-mono text-purple-400 font-semibold">Ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
