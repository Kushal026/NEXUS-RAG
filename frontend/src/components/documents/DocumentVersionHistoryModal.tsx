"use client";

import React from "react";
import {
  X,
  History,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  Tag,
  ArrowDown,
  Layers,
  ShieldCheck
} from "lucide-react";
import { DocumentInfo } from "../../types";

interface DocumentVersionHistoryModalProps {
  document: DocumentInfo;
  allDocuments: DocumentInfo[];
  onClose: () => void;
  onSelectVersion: (doc: DocumentInfo) => void;
}

export const DocumentVersionHistoryModal: React.FC<DocumentVersionHistoryModalProps> = ({
  document,
  allDocuments,
  onClose,
  onSelectVersion,
}) => {
  // Find all documents sharing the same lineage_id or base filename
  const baseName = document.filename.replace(/_v[0-9]+(?:\.[0-9]+)*|\.v[0-9]+(?:\.[0-9]+)*/i, "").replace(/\.[^/.]+$/, "");
  const familyDocs = allDocuments.filter((d) => {
    if (document.lineage_id && d.lineage_id) {
      return d.lineage_id === document.lineage_id;
    }
    const dBase = d.filename.replace(/_v[0-9]+(?:\.[0-9]+)*|\.v[0-9]+(?:\.[0-9]+)*/i, "").replace(/\.[^/.]+$/, "");
    return dBase === baseName;
  });

  // Sort versions ascending
  const sortedVersions = [...familyDocs].sort((a, b) => {
    const vA = a.version || "1.0.0";
    const vB = b.version || "1.0.0";
    return vA.localeCompare(vB, undefined, { numeric: true });
  });

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-panel p-6 rounded-2xl border border-slate-700 max-w-2xl w-full space-y-6 shadow-2xl animate-fadeIn">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Document Version Lineage</h3>
              <p className="text-xs text-slate-400">Family: {baseName}</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Version Timeline Path */}
        <div className="space-y-4">
          {sortedVersions.map((doc, idx) => {
            const isSelected = doc.id === document.id;
            const isLatest = doc.is_latest ?? (idx === sortedVersions.length - 1);

            return (
              <div
                key={doc.id}
                onClick={() => onSelectVersion(doc)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-4 ${
                  isSelected
                    ? "bg-indigo-950/40 border-indigo-500 shadow-md shadow-indigo-500/10"
                    : "bg-slate-950/70 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono text-xs font-bold ${
                      isLatest
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {doc.version || `v${idx + 1}.0`}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-200 truncate">
                        {doc.filename}
                      </span>
                      {isLatest ? (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold font-mono">
                          LATEST ACTIVE
                        </span>
                      ) : (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                          SUPERSEDED
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-0.5 font-mono">
                      <span>{doc.chunk_count} Chunks</span>
                      {doc.published_at && (
                        <span>Published: {new Date(doc.published_at).getFullYear()}</span>
                      )}
                      {doc.valid_from && (
                        <span>Valid: {new Date(doc.valid_from).getFullYear()}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="text-xs font-semibold text-indigo-400">
                  {isSelected ? "Current View" : "Inspect Version →"}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
