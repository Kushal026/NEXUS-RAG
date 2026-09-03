"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar, TabKey } from "../components/layout/Sidebar";
import { Header } from "../components/layout/Header";
import { CommandPalette } from "../components/layout/CommandPalette";
import { LandingPage } from "../components/landing/LandingPage";
import { AuthModal } from "../components/auth/AuthModal";
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
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();

  // "landing" vs "app"
  const [viewMode, setViewMode] = useState<"landing" | "app">("landing");
  const [activeTab, setActiveTab] = useState<TabKey>("dashboard");
  const [selectedDocument, setSelectedDocument] = useState<DocumentInfo | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  
  // UI Overlays
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<"signin" | "signup" | "forgot">("signin");

  // If user is authenticated, default to app view
  useEffect(() => {
    if (isAuthenticated) {
      setViewMode("app");
    }
  }, [isAuthenticated]);

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
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 10000);
    return () => clearInterval(interval);
  }, []);

  // Global Keyboard Shortcuts Listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle Command Palette on Cmd+K or Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
      // 'N' for New Research (when not typing in an input/textarea)
      if (
        e.key === "n" &&
        !["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName) &&
        !e.metaKey &&
        !e.ctrlKey
      ) {
        e.preventDefault();
        if (viewMode !== "app") setViewMode("app");
        setActiveTab("research");
        setSelectedDocument(null);
      }
      // '/' for focusing Search
      if (
        e.key === "/" &&
        !["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)
      ) {
        e.preventDefault();
        if (viewMode !== "app") setViewMode("app");
        setActiveTab("research");
        setSelectedDocument(null);
      }
      // Escape to close modals or document detail view
      if (e.key === "Escape") {
        if (commandPaletteOpen) {
          setCommandPaletteOpen(false);
        } else if (authModalOpen) {
          setAuthModalOpen(false);
        } else if (selectedDocument) {
          setSelectedDocument(null);
        } else if (mobileSidebarOpen) {
          setMobileSidebarOpen(false);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [commandPaletteOpen, authModalOpen, selectedDocument, mobileSidebarOpen, viewMode]);

  const handleSelectDocument = (doc: DocumentInfo) => {
    setSelectedDocument(doc);
    setActiveTab("documents");
  };

  const handleTabChange = (tab: TabKey) => {
    setSelectedDocument(null);
    setActiveTab(tab);
    setMobileSidebarOpen(false);
  };

  const handleStartResearch = (query?: string) => {
    if (isAuthenticated) {
      setViewMode("app");
      setActiveTab("research");
      setSelectedDocument(null);
    } else {
      setAuthModalMode("signin");
      setAuthModalOpen(true);
    }
  };

  const handleOpenAuth = (mode: "signin" | "signup" = "signin") => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  };

  // If user is on the Public Landing Page
  if (viewMode === "landing" && !isAuthenticated) {
    return (
      <>
        <LandingPage
          onStartResearch={() => handleStartResearch()}
          onOpenAuth={handleOpenAuth}
        />
        <AuthModal
          isOpen={authModalOpen}
          initialMode={authModalMode}
          onClose={() => setAuthModalOpen(false)}
          onSuccess={() => {
            setViewMode("app");
            setActiveTab("dashboard");
          }}
        />
      </>
    );
  }

  return (
    <div className="min-h-screen flex bg-[#f8fafc] text-slate-900 font-sans selection:bg-indigo-500/20 selection:text-indigo-800">
      {/* Desktop Collapsible Sidebar */}

      <div className="hidden md:block">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={handleTabChange}
          status={status}
          collapsed={sidebarCollapsed}
          setCollapsed={setSidebarCollapsed}
          onOpenCommandPalette={() => setCommandPaletteOpen(true)}
        />
      </div>

      {/* Mobile Drawer Sidebar */}
      <AnimatePresence>
        {mobileSidebarOpen && (
          <div className="fixed inset-0 z-50 md:hidden flex">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileSidebarOpen(false)}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="relative z-10 w-72 h-full"
            >
              <Sidebar
                activeTab={activeTab}
                setActiveTab={handleTabChange}
                status={status}
                collapsed={false}
                setCollapsed={() => {}}
                onOpenCommandPalette={() => {
                  setMobileSidebarOpen(false);
                  setCommandPaletteOpen(true);
                }}
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Global Command Palette (⌘K) */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={(tab) => {
          setViewMode("app");
          handleTabChange(tab);
        }}
        onStartResearch={(query) => {
          setViewMode("app");
          setActiveTab("research");
        }}
      />

      {/* Auth Modal for re-authentication or switching */}
      <AuthModal
        isOpen={authModalOpen}
        initialMode={authModalMode}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={() => {
          setViewMode("app");
          fetchState();
        }}
      />

      {/* Main Content Workspace Column */}
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden min-h-screen">
        {/* Modern Linear-style Header Bar */}
        <Header
          activeTab={activeTab}
          status={status}
          onOpenCommandPalette={() => setCommandPaletteOpen(true)}
          onToggleMobileSidebar={() => setMobileSidebarOpen(true)}
          onNewResearch={() => handleTabChange("research")}
          onUploadDocument={() => handleTabChange("documents")}
          onViewLanding={() => setViewMode("landing")}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 p-4 md:p-8 max-w-[1700px] w-full mx-auto">
          {loadingDocs && !status ? (
            <div className="flex items-center justify-center min-h-[60vh]">
              <div className="text-center space-y-4">
                <div className="relative w-12 h-12 mx-auto">
                  <div className="w-12 h-12 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                  </div>
                </div>
                <p className="text-xs font-mono text-slate-400">
                  Initializing NEXUS Neural Engine...
                </p>
              </div>
            </div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab + (selectedDocument ? `-${selectedDocument.id}` : "")}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
              >
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
              </motion.div>
            </AnimatePresence>
          )}
        </main>

        {/* Professional Minimalist Footer */}
        <footer className="border-t border-slate-200/80 py-3.5 px-6 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3 bg-white/90 backdrop-blur-md">
          <div className="flex items-center gap-2.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium text-slate-800">NEXUS Evidence & Knowledge Platform</span>
            <span className="text-slate-300">•</span>
            <span className="text-slate-500 font-mono text-[11px]">{documents.length} Docs Indexed</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-slate-500">
            <span>Hybrid Dense-Sparse RRF</span>
            <span>•</span>
            <span>NLI Contradiction Engine</span>
            <span>•</span>
            <span>Multi-User Isolated</span>
          </div>
        </footer>

      </div>
    </div>
  );
}
