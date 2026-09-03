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
import { SystemStatus, DocumentInfo } from "../types";
import { api } from "../services/api";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "documents" | "research" | "graph" | "evaluation" | "settings">("dashboard");
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

  const handleTabChange = (tab: "dashboard" | "documents" | "research" | "graph" | "evaluation" | "settings") => {
    setSelectedDocument(null);
    setActiveTab(tab);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      {/* Navigation Header */}
      <Navbar status={status} activeTab={activeTab} setActiveTab={handleTabChange} />

      {/* Main Page Content Area */}
      <main className="flex-1 p-6 md:p-8 max-w-[1600px] w-full mx-auto">
        {selectedDocument ? (
          <DocumentDetailsView
            document={selectedDocument}
            onBack={() => setSelectedDocument(null)}
          />
        ) : (
          <>
            {activeTab === "dashboard" && (
              <DashboardOverview
                status={status}
                documents={documents}
                onNavigate={handleTabChange}
                onSelectDocument={handleSelectDocument}
              />
            )}

            {activeTab === "documents" && (
              <DocumentVault
                documents={documents}
                onRefresh={fetchState}
              />
            )}

            {activeTab === "research" && (
              <ResearchWorkbench documents={documents} />
            )}

            {activeTab === "graph" && (
              <KnowledgeGraphView documents={documents} />
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
          <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
          <span>NEXUS-RAG Advanced Hybrid Retrieval & Knowledge Graph Engine • Phase 5 Active</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Neo4j Dual-Engine Active</span>
          <span>•</span>
          <span>Zero-Hallucination Provenance Architecture</span>
        </div>
      </footer>
    </div>
  );
}

