"use client";

import React, { useState } from "react";
import {
  UploadCloud,
  FileText,
  Trash2,
  Eye,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  FileSpreadsheet,
  FileCode,
  File,
  X
} from "lucide-react";
import { DocumentInfo, DocumentChunk } from "../../types";
import { api } from "../../services/api";

import { DocumentVersionHistoryModal } from "./DocumentVersionHistoryModal";
import { History } from "lucide-react";

interface DocumentVaultProps {
  documents: DocumentInfo[];
  onRefresh: () => void;
}

export const DocumentVault: React.FC<DocumentVaultProps> = ({ documents, onRefresh }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentInfo | null>(null);
  const [versionModalDoc, setVersionModalDoc] = useState<DocumentInfo | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadError(null);

    try {
      for (let i = 0; i < files.length; i++) {
        await api.uploadDocument(files[i]);
      }
      onRefresh();
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload file");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleViewChunks = async (doc: DocumentInfo) => {
    setSelectedDoc(doc);
    setLoadingChunks(true);
    try {
      const data = await api.getDocumentChunks(doc.id);
      setChunks(data);
    } catch (err) {
      console.error(err);
      setChunks([]);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to remove this document and its indexed vectors from the vault?")) return;
    try {
      await api.deleteDocument(docId);
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null);
        setChunks([]);
      }
      onRefresh();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case "pdf":
        return <FileText className="w-5 h-5 text-rose-400" />;
      case "csv":
        return <FileSpreadsheet className="w-5 h-5 text-emerald-400" />;
      case "docx":
      case "doc":
        return <FileText className="w-5 h-5 text-blue-400" />;
      case "md":
      case "markdown":
      case "html":
        return <FileCode className="w-5 h-5 text-amber-400" />;
      default:
        return <File className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Upload Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <UploadCloud className="w-5 h-5 text-indigo-400" />
              Document Ingestion & Vault
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Ingest multi-format evidence documents. The engine performs structure-aware parsing, extracts section hierarchies, calculates semantic chunk spans, and computes dual-index representations (Dense Embeddings + BM25 Lexical Tokens).
            </p>
            <div className="flex items-center gap-2 mt-3 text-[11px] text-slate-400 font-mono">
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">PDF (PyMuPDF)</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">DOCX</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">Markdown / TXT</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">HTML</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">CSV</span>
            </div>
          </div>

          <label className="cursor-pointer flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-lg shadow-indigo-600/30 transition-all">
            <UploadCloud className="w-4 h-4" />
            {uploading ? "Ingesting & Indexing..." : "Upload Evidence Documents"}
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.doc,.txt,.md,.markdown,.html,.htm,.csv,.json"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>

        {uploadError && (
          <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Grid: Document List & Chunk Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Document List */}
        <div className={`space-y-3 ${selectedDoc ? "lg:col-span-5" : "lg:col-span-12"}`}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Indexed Documents ({documents.length})
            </h3>
          </div>

          {documents.length === 0 ? (
            <div className="p-12 text-center glass-panel rounded-2xl border border-slate-800/80">
              <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-sm font-medium text-slate-300">No documents in knowledge vault</p>
              <p className="text-xs text-slate-500 mt-1">Upload PDF, DOCX, Markdown, or CSV files to begin.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => {
                const isSelected = selectedDoc?.id === doc.id;
                return (
                  <div
                    key={doc.id}
                    className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                      isSelected
                        ? "bg-slate-900 border-indigo-500/50 shadow-md shadow-indigo-500/10"
                        : "glass-panel hover:bg-slate-900/60 border-slate-800"
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 shrink-0">
                        {getFileIcon(doc.file_type)}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs font-semibold text-slate-100 truncate">{doc.filename}</h4>
                          <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                            {doc.version || "v1.0"}
                          </span>
                          {doc.is_latest === false ? (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono">
                              SUPERSEDED
                            </span>
                          ) : (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 font-mono">
                              LATEST
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-1">
                          <span className="uppercase font-mono text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                            {doc.file_type}
                          </span>
                          <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                          {doc.page_count && <span>{doc.page_count} pages</span>}
                          <span className="flex items-center gap-1 text-indigo-400 font-medium">
                            <Layers className="w-3 h-3" />
                            {doc.chunk_count} chunks
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        onClick={() => setVersionModalDoc(doc)}
                        className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center gap-1 transition-all"
                        title="View Document Version Lineage"
                      >
                        <History className="w-3.5 h-3.5 text-indigo-400" />
                        <span className="hidden sm:inline">Lineage</span>
                      </button>
                      <button
                        onClick={() => handleViewChunks(doc)}
                        className={`p-2 rounded-lg text-xs font-medium flex items-center gap-1 transition-all ${
                          isSelected
                            ? "bg-indigo-600 text-white"
                            : "bg-slate-800 hover:bg-slate-700 text-slate-200"
                        }`}
                        title="Inspect Extracted Chunks"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Chunks</span>
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-2 rounded-lg bg-slate-800/80 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-all"
                        title="Delete Document & Index"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Version History Modal */}
        {versionModalDoc && (
          <DocumentVersionHistoryModal
            document={versionModalDoc}
            allDocuments={documents}
            onClose={() => setVersionModalDoc(null)}
            onSelectVersion={(selected) => {
              setVersionModalDoc(null);
              handleViewChunks(selected);
            }}
          />
        )}

        {/* Live Semantic Chunk Inspector */}
        {selectedDoc && (
          <div className="lg:col-span-7 space-y-4">
            <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    Chunk Structure Inspector: {selectedDoc.filename}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Viewing {chunks.length} extracted semantic chunk spans with boundary metadata.
                  </p>
                </div>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {loadingChunks ? (
                <div className="p-8 text-center text-xs text-slate-400">Loading chunk representations...</div>
              ) : chunks.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-400">No chunks available for this document.</div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                  {chunks.map((chunk, idx) => (
                    <div
                      key={chunk.id}
                      className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/90 text-xs space-y-2 hover:border-slate-700 transition-all"
                    >
                      <div className="flex items-center justify-between text-[11px] text-slate-400 pb-1.5 border-b border-slate-850">
                        <div className="flex items-center gap-2 font-mono">
                          <span className="text-indigo-400 font-semibold">Chunk #{idx + 1}</span>
                          <span className="text-slate-500">|</span>
                          <span>
                            Span: [
                            {chunk.start_char ?? chunk.span?.start_char ?? 0}..
                            {chunk.end_char ?? chunk.span?.end_char ?? chunk.content.length}
                            ]
                          </span>
                          {(chunk.page_number || chunk.span?.page_number) && (
                            <>
                              <span className="text-slate-500">|</span>
                              <span className="text-cyan-400">
                                Page {chunk.page_number || chunk.span?.page_number}
                              </span>
                            </>
                          )}
                        </div>
                        {(chunk.section_title || chunk.span?.section_title) && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 truncate max-w-[200px]">
                            {chunk.section_title || chunk.span?.section_title}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-200 text-xs font-mono leading-relaxed whitespace-pre-wrap">
                        {chunk.content}
                      </p>
                      <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                        <span>Tokens: ~{chunk.content.split(/\s+/).length}</span>
                        <span className="font-mono text-slate-600 truncate max-w-[150px]">ID: {chunk.id}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
