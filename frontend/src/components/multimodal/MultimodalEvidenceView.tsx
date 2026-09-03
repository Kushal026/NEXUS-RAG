"use client";

import React, { useState } from "react";
import {
  Layers,
  Table as TableIcon,
  BarChart3,
  Code2,
  FileImage,
  FileText,
  Search,
  Sparkles,
  ExternalLink,
  Copy,
  Check,
  CheckCircle2,
  Clock,
  ShieldCheck,
  ChevronRight,
  Filter,
  Eye,
  Database
} from "lucide-react";
import { api } from "@/services/api";
import {
  MultimodalRetrievalResult,
  MultimodalEvidenceItem,
  ModalityType,
  MultimodalDocumentRepresentation
} from "@/types";

export const MultimodalEvidenceView: React.FC = () => {
  const [query, setQuery] = useState("");
  const [selectedModality, setSelectedModality] = useState<string>("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MultimodalRetrievalResult | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeDocTree, setActiveDocTree] = useState<MultimodalDocumentRepresentation | null>(null);
  const [showTreeModal, setShowTreeModal] = useState(false);

  const presets = [
    { label: "Transformer Accuracy Table", query: "Transformer model benchmark accuracy table across datasets", mod: "table" },
    { label: "Attention Latency Chart", query: "Multi-head attention training latency versus sequence length figure", mod: "figure" },
    { label: "PyTorch Attention Code", query: "PyTorch scaled dot product attention mechanism code implementation", mod: "code" },
    { label: "Scanned Architecture Diagram", query: "Scanned transformer system architecture diagram and layout", mod: "image" }
  ];

  const handleSearch = async (overrideQuery?: string, overrideModality?: string) => {
    const q = overrideQuery !== undefined ? overrideQuery : query;
    const mod = overrideModality !== undefined ? overrideModality : selectedModality;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await api.queryMultimodalEvidence(q, mod, 10);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to retrieve multimodal evidence");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = (id: string, code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleInspectDocumentTree = async (sampleText: string, filename: string) => {
    try {
      const parsed = await api.parseMultimodalText(sampleText, filename);
      setActiveDocTree(parsed);
      setShowTreeModal(true);
    } catch (err: any) {
      console.error(err);
    }
  };

  const getModalityIcon = (mod: ModalityType) => {
    switch (mod) {
      case "table":
        return <TableIcon className="w-4 h-4 text-emerald-400" />;
      case "figure":
      case "chart":
        return <BarChart3 className="w-4 h-4 text-cyan-400" />;
      case "code":
        return <Code2 className="w-4 h-4 text-amber-400" />;
      case "image":
        return <FileImage className="w-4 h-4 text-violet-400" />;
      default:
        return <FileText className="w-4 h-4 text-indigo-400" />;
    }
  };

  const getModalityBadgeStyle = (mod: ModalityType) => {
    switch (mod) {
      case "table":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "figure":
      case "chart":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "code":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "image":
        return "bg-violet-500/10 text-violet-400 border-violet-500/30";
      default:
        return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-violet-900/40 via-purple-900/20 to-slate-900/40 border border-violet-800/40 p-6 backdrop-blur-xl shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/30 uppercase tracking-wide">
                Multimodal Engine
              </span>

              <span className="text-xs text-slate-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Zero Costly LLM Vision Calls
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Layers className="w-7 h-7 text-violet-400" />
              Multimodal Evidence Intelligence Engine
            </h2>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Cross-modality retrieval across structured tables, charts, axes/values, OCR scans, code blocks, and text passages with strict provenance tracking.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-xl border border-slate-800/80">
            <div className="text-right px-2">
              <p className="text-[11px] text-slate-400">Supported Modalities</p>
              <p className="text-xs font-semibold text-slate-200">PDF, Tables, Charts, OCR, Code, CSV, DOCX</p>
            </div>
          </div>
        </div>
      </div>

      {/* Query Bar & Presets */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4 backdrop-blur-md">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search across tables, charts, figures, OCR text, or code implementations..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all"
            />
          </div>

          {/* Modality Filter Dropdown / Buttons */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 overflow-x-auto">
            {[
              { id: "all", label: "All Modalities", icon: Layers },
              { id: "table", label: "Tables", icon: TableIcon },
              { id: "figure", label: "Charts / Figs", icon: BarChart3 },
              { id: "code", label: "Code", icon: Code2 },
              { id: "image", label: "OCR / Images", icon: FileImage },
              { id: "text", label: "Text", icon: FileText }
            ].map((m) => {
              const Icon = m.icon;
              return (
                <button
                  key={m.id}
                  onClick={() => {
                    setSelectedModality(m.id);
                    if (query.trim()) handleSearch(query, m.id);
                  }}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                    selectedModality === m.id
                      ? "bg-violet-600 text-white shadow-md shadow-violet-600/30"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {m.label}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => handleSearch()}
            disabled={loading || !query.trim()}
            className="px-6 py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:opacity-50 text-white rounded-xl text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-violet-600/20 transition-all cursor-pointer"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Retrieve
              </>
            )}
          </button>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400 pt-1">
          <span className="text-[11px] font-medium text-slate-500 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Quick Modality Queries:
          </span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(p.query);
                setSelectedModality(p.mod);
                handleSearch(p.query, p.mod);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-violet-500/40 text-slate-300 text-[11px] transition-all"
            >
              {p.label}
            </button>
          ))}
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
          {/* Metrics & Modality Distribution Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium">Total Items</p>
              <p className="text-lg font-bold text-white mt-0.5">{result.evidence_items.length}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                <TableIcon className="w-3 h-3" /> Tables
              </p>
              <p className="text-lg font-bold text-emerald-300 mt-0.5">{result.modality_counts.table || 0}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-cyan-400 font-medium flex items-center gap-1">
                <BarChart3 className="w-3 h-3" /> Figures / Charts
              </p>
              <p className="text-lg font-bold text-cyan-300 mt-0.5">{result.modality_counts.figure || 0}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-amber-400 font-medium flex items-center gap-1">
                <Code2 className="w-3 h-3" /> Code Blocks
              </p>
              <p className="text-lg font-bold text-amber-300 mt-0.5">{result.modality_counts.code || 0}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-violet-400 font-medium flex items-center gap-1">
                <FileImage className="w-3 h-3" /> Images / OCR
              </p>
              <p className="text-lg font-bold text-violet-300 mt-0.5">{result.modality_counts.image || 0}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <p className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
                <Clock className="w-3 h-3" /> Latency
              </p>
              <p className="text-lg font-bold text-slate-200 mt-0.5">{result.execution_time_ms} ms</p>
            </div>
          </div>

          {/* Multimodal Evidence Cards Grid */}
          <div className="space-y-4">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-violet-400" />
              Retrieved Multimodal Evidence Items ({result.evidence_items.length})
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.evidence_items.map((item) => (
                <div
                  key={item.evidence_id}
                  className="rounded-xl bg-slate-900/80 border border-slate-800/80 p-5 space-y-4 backdrop-blur-md shadow-lg hover:border-slate-700 transition-all flex flex-col justify-between"
                >
                  {/* Top Bar: Modality Badge & Provenance */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase flex items-center gap-1.5 border ${getModalityBadgeStyle(item.modality)}`}>
                          {getModalityIcon(item.modality)}
                          {item.modality}
                        </span>
                        <span className="text-[11px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                          Score: {item.relevance_score.toFixed(3)}
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 font-mono">
                        Page {item.page_number || 1}
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-white tracking-tight">
                      {item.title || item.caption || "Multimodal Asset"}
                    </h4>
                  </div>

                  {/* Body Content per Modality */}
                  <div className="flex-1">
                    {/* TABLE PREVIEW */}
                    {item.modality === "table" && item.table_data && (
                      <div className="space-y-2">
                        <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/60 max-h-48">
                          <table className="w-full text-xs text-left text-slate-300">
                            <thead className="text-[11px] uppercase bg-slate-800/80 text-slate-300 border-b border-slate-700">
                              <tr>
                                {item.table_data.headers.map((h, i) => (
                                  <th key={i} className="px-3 py-2 font-semibold">
                                    {h}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {item.table_data.rows.slice(0, 5).map((r, ri) => (
                                <tr key={ri} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                                  {r.map((c, ci) => (
                                    <td key={ci} className="px-3 py-1.5 font-mono text-[11px] text-slate-300">
                                      {c}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <p className="text-[10px] text-slate-400">
                          {item.table_data.num_rows} rows × {item.table_data.num_cols} columns
                        </p>
                      </div>
                    )}

                    {/* FIGURE / CHART PREVIEW */}
                    {(item.modality === "figure" || item.modality === "chart") && item.chart_data && (
                      <div className="space-y-2.5 bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
                        <div className="flex flex-wrap gap-2 text-xs">
                          {item.chart_data.x_axis_label && (
                            <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-[11px]">
                              X-Axis: <strong className="text-white">{item.chart_data.x_axis_label}</strong>
                            </span>
                          )}
                          {item.chart_data.y_axis_label && (
                            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20 text-[11px]">
                              Y-Axis: <strong className="text-white">{item.chart_data.y_axis_label}</strong>
                            </span>
                          )}
                        </div>

                        {item.chart_data.visible_values.length > 0 && (
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-[10px] uppercase font-semibold text-slate-500">Values:</span>
                            {item.chart_data.visible_values.map((v, vi) => (
                              <span key={vi} className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-cyan-200">
                                {v}
                              </span>
                            ))}
                          </div>
                        )}

                        <p className="text-xs text-slate-300 line-clamp-3">
                          {item.chart_data.explanatory_text}
                        </p>
                      </div>
                    )}

                    {/* CODE PREVIEW */}
                    {item.modality === "code" && item.code_data && (
                      <div className="space-y-2">
                        <div className="relative rounded-lg bg-slate-950 border border-slate-800 p-3 font-mono text-xs text-amber-200/90 overflow-x-auto max-h-48">
                          <button
                            onClick={() => handleCopyCode(item.evidence_id, item.code_data!.code_content)}
                            className="absolute top-2 right-2 p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
                          >
                            {copiedId === item.evidence_id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                          </button>
                          <pre>{item.code_data.code_content}</pre>
                        </div>
                        <span className="text-[10px] uppercase font-semibold text-amber-400/80">
                          Language: {item.code_data.language}
                        </span>
                      </div>
                    )}

                    {/* IMAGE / OCR PREVIEW */}
                    {item.modality === "image" && (
                      <div className="space-y-2 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                        <div className="flex items-center gap-2 text-xs text-violet-400">
                          <FileImage className="w-4 h-4" />
                          <span>Visual Scan OCR Extraction</span>
                        </div>
                        <p className="text-xs font-mono text-slate-300 bg-slate-900/60 p-2.5 rounded border border-slate-800/60 whitespace-pre-wrap">
                          {item.content_snippet}
                        </p>
                      </div>
                    )}

                    {/* TEXT PREVIEW */}
                    {item.modality === "text" && (
                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                        {item.content_snippet}
                      </p>
                    )}
                  </div>

                  {/* Strict Provenance Footer Pill */}
                  <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                    <span className="px-2.5 py-1 rounded-full bg-slate-950 text-slate-300 border border-slate-800 font-mono text-[11px] flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      {item.provenance_label}
                    </span>

                    <button
                      onClick={() => handleInspectDocumentTree(item.content_snippet, item.document_filename)}
                      className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1 font-medium"
                    >
                      Inspect Tree <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Document Hierarchy Tree Modal */}
      {showTreeModal && activeDocTree && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-violet-400" />
                <h3 className="text-base font-bold text-white">
                  Document Representation Hierarchy: {activeDocTree.filename}
                </h3>
              </div>
              <button
                onClick={() => setShowTreeModal(false)}
                className="text-slate-400 hover:text-white text-xs px-2.5 py-1 rounded-lg bg-slate-800"
              >
                Close
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs text-slate-300 bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-y-auto max-h-96">
              <p className="text-violet-400 font-bold">Document: {activeDocTree.filename}</p>
              <p className="pl-4 text-slate-400">├── 📝 Text Chunks ({activeDocTree.text_chunks.length})</p>
              <p className="pl-4 text-emerald-400">├── 📊 Tables ({activeDocTree.tables.length})</p>
              {activeDocTree.tables.map((t, i) => (
                <p key={i} className="pl-8 text-emerald-300/80">└── Table {i + 1}: {t.caption} ({t.num_rows}r × {t.num_cols}c, P.{t.source_page})</p>
              ))}
              <p className="pl-4 text-cyan-400">├── 📈 Figures & Charts ({activeDocTree.figures.length})</p>
              {activeDocTree.figures.map((f, i) => (
                <p key={i} className="pl-8 text-cyan-300/80">└── Figure {i + 1}: {f.title} (Type: {f.figure_type}, P.{f.source_page})</p>
              ))}
              <p className="pl-4 text-amber-400">├── 💻 Code Blocks ({activeDocTree.code_blocks.length})</p>
              {activeDocTree.code_blocks.map((c, i) => (
                <p key={i} className="pl-8 text-amber-300/80">└── Code {i + 1}: {c.language.toUpperCase()} (P.{c.source_page})</p>
              ))}
              <p className="pl-4 text-violet-400">├── 🖼 Images & OCR ({activeDocTree.images.length})</p>
              <p className="pl-4 text-slate-400">├── 🏷 Metadata ({activeDocTree.metadata.file_type}, {activeDocTree.metadata.file_size} bytes)</p>
              <p className="pl-4 text-slate-400">└── 📚 References ({activeDocTree.references.length})</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
