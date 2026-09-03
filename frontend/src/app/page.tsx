"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/layout/Navbar";
import { DashboardOverview } from "../components/dashboard/DashboardOverview";
import { DocumentVault } from "../components/documents/DocumentVault";
import { DocumentDetailsView } from "../components/documents/DocumentDetailsView";
import { ResearchWorkbench } from "../components/research/ResearchWorkbench";
import { EvaluationDashboard } from "../components/evaluation/EvaluationDashboard";
import { SettingsView } from "../components/settings/SettingsView";
import { KnowledgeGraphView } from "../components/graph/KnowledgeGraphView";
import { EvidenceInspector } from "../components/evidence/EvidenceInspector";
import { SelfCorrectingWorkbench } from "../components/self_correction/SelfCorrectingWorkbench";
import { MultimodalEvidenceView } from "../components/multimodal/MultimodalEvidenceView";
import { ResearchAgentWorkbench } from "../components/agent/ResearchAgentWorkbench";
import { SystemStatus, DocumentInfo } from "../types";
import { api } from "../services/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "documents" | "research" | "graph" | "evidence" | "self-correcting" | "multimodal" | "agent" | "evaluation" | "settings">("dashboard");
  const [selectedDocument, setSelectedDocument] = useState<DocumentInfo | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchState = async () => {
    try {
      const [statusRes, docsRes] = await Promise.all([
        api.getSystemStatus().catch(() => null),
        api.listDocuments().catch(() => []),
      ]);
      if (statusRes) setStatus(statusRes);
      setDocuments(docsRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectDocument = (doc: DocumentInfo) => {
    setSelectedDocument(doc);
  };

  const handleTabChange = (tab: "dashboard" | "documents" | "research" | "graph" | "evidence" | "self-correcting" | "multimodal" | "agent" | "evaluation" | "settings") => {
    setSelectedDocument(null);
    setActiveTab(tab);
  };


  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      {/* Navigation Header */}
      <Navbar status={status} activeTab={activeTab} setActiveTab={handleTabChange} />

      {/* Main Page Content Area */}
      <main className="flex-1 p-6 md:p-8 max-w-[1600px] w-full mx-auto">
        {loading && !status ? (
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto" />
              <p className="text-sm text-slate-400 font-medium">Initializing NEXUS-RAG Core Engine...</p>
            </div>
          </div>
        ) : (
          <>
            {activeTab === "dashboard" && (
              <DashboardOverview
                status={status}
                documents={documents}
                onSelectDocument={handleSelectDocument}
                onNavigate={(tab: any) => handleTabChange(tab)}
              />
            )}

            {activeTab === "documents" && (
              selectedDocument ? (
                <DocumentDetailsView
                  document={selectedDocument}
                  onBack={() => setSelectedDocument(null)}
                />

              ) : (
                <DocumentVault
                  documents={documents}
                  onSelectDocument={handleSelectDocument}
                  onUploadSuccess={fetchState}
                />
              )
            )}

            {activeTab === "research" && (
              <ResearchWorkbench
                documents={documents}
                onNavigateToDocs={() => handleTabChange("documents")}
              />
            )}

            {activeTab === "graph" && (
              <KnowledgeGraphView documents={documents} />
            )}

            {activeTab === "evidence" && (
              <EvidenceInspector documents={documents} />
            )}

            {activeTab === "self-correcting" && (
              <SelfCorrectingWorkbench documents={documents} />
            )}

            {activeTab === "multimodal" && (
              <MultimodalEvidenceView />
            )}

            {activeTab === "agent" && (
              <ResearchAgentWorkbench documents={documents} />
            )}

            {activeTab === "evaluation" && (
              <EvaluationDashboard />
            )}

            {activeTab === "settings" && (
              <SettingsView status={status} />
            )}

          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2 bg-slate-950/80">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
          <span>NEXUS-RAG Multimodal Evidence & Knowledge Graph Engine • Phase 8 Active</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Cross-Modality Retrieval</span>
          <span>•</span>
          <span>Structured Tables & Charts</span>
          <span>•</span>
          <span>Strict Citation Provenance</span>
        </div>
      </footer>
    </div>
  );
}
