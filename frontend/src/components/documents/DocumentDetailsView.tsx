"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Layers,
  ArrowLeft,
  Calendar,
  HardDrive,
  FileCode,
  Eye,
  CheckCircle2,
  BookOpen,
  Search
} from "lucide-react";
import { DocumentInfo, DocumentChunk } from "../../types";
import { api } from "../../services/api";

interface DocumentDetailsViewProps {
  document: DocumentInfo;
  onBack: () => void;
}

export const DocumentDetailsView: React.FC<DocumentDetailsViewProps> = ({
  document,
  onBack,
}) => {
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedChunk, setSelectedChunk] = useState<DocumentChunk | null>(null);
  const [activeTab, setActiveTab] = useState<"chunks" | "content">("chunks");
  const [chunkFilter, setChunkFilter] = useState("");

  useEffect(() => {
    const fetchChunks = async () => {
      setLoading(true);
      try {
        const data = await api.getDocumentChunks(document.id);
        setChunks(data);
        if (data.length > 0) setSelectedChunk(data[0]);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchChunks();
  }, [document.id]);

  const filteredChunks = chunks.filter((c) =>
    c.content.toLowerCase().includes(chunkFilter.toLowerCase()) ||
    (c.span?.section_title && c.span.section_title.toLowerCase().includes(chunkFilter.toLowerCase())) ||
    (c.section_title && c.section_title.toLowerCase().includes(chunkFilter.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Navigation & Meta Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight">{document.filename}</h2>
                <span className="uppercase font-mono text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {document.file_type}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Document ID: <span className="font-mono text-slate-300">{document.id}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-xl border border-slate-850 text-xs">
            <button
              onClick={() => setActiveTab("chunks")}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === "chunks"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Extracted Chunks ({chunks.length})
            </button>
            <button
              onClick={() => setActiveTab("content")}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === "content"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Source Text Preview
            </button>
          </div>
        </div>

        {/* Metadata Chips */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-850 text-xs text-slate-300">
          <div className="flex items-center gap-2">
            <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
            <span>Size: <strong>{(document.file_size / 1024).toFixed(1)} KB</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Chunks: <strong>{document.chunk_count}</strong></span>
          </div>
          {document.page_count && (
            <div className="flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-purple-400" />
              <span>Pages: <strong>{document.page_count}</strong></span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            <span>Ingested: <strong>{new Date(document.created_at).toLocaleDateString()}</strong></span>
          </div>
        </div>
      </div>

      {/* Main View Area */}
      {activeTab === "chunks" ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Chunk Selector List */}
          <div className="lg:col-span-5 space-y-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={chunkFilter}
                onChange={(e) => setChunkFilter(e.target.value)}
                placeholder="Filter chunks by text or section..."
                className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all font-mono"
              />
            </div>

            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading semantic chunks...</div>
            ) : filteredChunks.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No chunks matching filter.</div>
            ) : (
              <div className="space-y-2 max-h-[620px] overflow-y-auto pr-1">
                {filteredChunks.map((chunk) => {
                  const isSelected = selectedChunk?.id === chunk.id;
                  return (
                    <div
                      key={chunk.id}
                      onClick={() => setSelectedChunk(chunk)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-slate-900 border-indigo-500 shadow-md shadow-indigo-500/10"
                          : "glass-panel hover:bg-slate-900/60 border-slate-800"
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs pb-1.5 border-b border-slate-800/80">
                        <span className="font-bold text-indigo-400 font-mono">
                          Chunk #{chunk.chunk_index + 1}
                        </span>
                        {(chunk.page_number || chunk.span?.page_number) && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 font-mono">
                            Page {chunk.page_number || chunk.span?.page_number}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-300 line-clamp-2 mt-2 font-mono">
                        {chunk.content}
                      </p>
                      {(chunk.section_title || chunk.span?.section_title) && (
                        <span className="inline-block mt-2 text-[10px] text-slate-400 font-sans truncate max-w-[220px]">
                          § {chunk.section_title || chunk.span?.section_title}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Selected Chunk Deep Inspector */}
          {selectedChunk && (
            <div className="lg:col-span-7 space-y-4">
              <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    Chunk #{selectedChunk.chunk_index + 1} Metadata & Bounds
                  </h3>
                  <span className="text-xs font-mono text-slate-400">
                    ID: {selectedChunk.id.substring(0, 16)}...
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-850 space-y-1">
                    <span className="text-slate-400">Character Range</span>
                    <p className="font-mono text-indigo-400 font-bold">
                      [{selectedChunk.start_char ?? selectedChunk.span?.start_char ?? 0} ..{" "}
                      {selectedChunk.end_char ?? selectedChunk.span?.end_char ?? selectedChunk.content.length}]
                    </p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-850 space-y-1">
                    <span className="text-slate-400">Token Estimate</span>
                    <p className="font-mono text-cyan-400 font-bold">
                      ~{selectedChunk.content.split(/\s+/).length} tokens
                    </p>
                  </div>
                </div>

                {(selectedChunk.section_title || selectedChunk.span?.section_title) && (
                  <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-850 text-xs">
                    <span className="text-slate-400">Hierarchical Section Title:</span>
                    <p className="font-medium text-slate-200 mt-0.5">
                      {selectedChunk.section_title || selectedChunk.span?.section_title}
                    </p>
                  </div>
                )}

                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-300">Chunk Text Content:</span>
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 leading-relaxed max-h-[380px] overflow-y-auto whitespace-pre-wrap">
                    {selectedChunk.content}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Source Text Preview Tab */
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <FileCode className="w-4 h-4 text-emerald-400" />
            Raw Ingested Text Extract
          </h3>
          <p className="text-xs text-slate-400">
            Preview of parsed textual representation preserved for semantic retrieval and chunk boundary calculation.
          </p>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 leading-relaxed max-h-[500px] overflow-y-auto whitespace-pre-wrap">
            {document.content_preview || "Document text available in indexed chunk representations."}
          </div>
        </div>
      )}
    </div>
  );
};
