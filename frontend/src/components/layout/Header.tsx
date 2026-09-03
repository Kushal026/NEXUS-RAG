"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Search,
  Plus,
  Activity,
  Zap,
  Menu,
  Database,
  Cpu,
  ShieldCheck,
  Command,
  FileUp,
  User,
  LogOut,
  ChevronDown,
  Globe,
  Sliders
} from "lucide-react";
import { SystemStatus } from "../../types";
import { TabKey } from "./Sidebar";
import { useAuth } from "../../context/AuthContext";

interface HeaderProps {
  activeTab: TabKey;
  status: SystemStatus | null;
  onOpenCommandPalette: () => void;
  onToggleMobileSidebar: () => void;
  onNewResearch: () => void;
  onUploadDocument: () => void;
  onViewLanding?: () => void;
}

const TAB_TITLES: Record<TabKey, { title: string; subtitle: string }> = {
  dashboard: { title: "Platform Overview", subtitle: "System architecture, health telemetry & vault metrics" },
  documents: { title: "Document Vault", subtitle: "Multi-format ingestion, chunk inspector & provenance" },
  research: { title: "Research & Synthesis", subtitle: "Dual-index semantic retrieval with claim-level citations" },
  graph: { title: "Knowledge Graph Traversal", subtitle: "Entity relationship navigation & multi-hop discovery" },
  evidence: { title: "Evidence Intelligence", subtitle: "NLI contradiction detection & source reliability scoring" },
  "self-correcting": { title: "Self-Correcting Engine", subtitle: "Iterative recovery with query rewriting & answer verification" },
  multimodal: { title: "Multimodal Evidence Engine", subtitle: "Cross-modality retrieval for tables, charts, figures & OCR" },
  agent: { title: "Autonomous Research Agent", subtitle: "Goal planning, gap detection & comprehensive report compilation" },
  evaluation: { title: "IR & Query Benchmark Suite", subtitle: "Recall@K, MRR, NDCG and reasoning evaluations" },
  settings: { title: "Model & System Settings", subtitle: "Embedding providers, reranker configurations & search parameters" },
};

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  status,
  onOpenCommandPalette,
  onToggleMobileSidebar,
  onNewResearch,
  onUploadDocument,
  onViewLanding,
}) => {
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentTab = TAB_TITLES[activeTab] || { title: "NEXUS", subtitle: "AI Research Platform" };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getInitials = (name?: string, username?: string) => {
    if (name) {
      const parts = name.split(" ");
      return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
    }
    return (username || "U").slice(0, 2).toUpperCase();
  };

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between px-6 py-3 border-b border-slate-200/90 bg-white/85 backdrop-blur-xl h-16 shadow-xs">
      {/* Left: Mobile Menu & Current Tab Title */}
      <div className="flex items-center gap-4 min-w-0">
        <button
          onClick={onToggleMobileSidebar}
          className="p-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-600 hover:text-slate-900 md:hidden"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-indigo-600">NEXUS</span>
            <span className="text-slate-400">/</span>
            <h1 className="text-sm font-bold text-slate-900 tracking-tight truncate">
              {currentTab.title}
            </h1>
          </div>
          <p className="text-[11px] text-slate-500 truncate hidden sm:block">
            {currentTab.subtitle}
          </p>
        </div>
      </div>

      {/* Center/Right: Omni-Search Trigger, Quick Actions, and Profile Menu */}
      <div className="flex items-center gap-3">
        {/* Global Command Bar Button */}
        <button
          onClick={onOpenCommandPalette}
          className="hidden md:flex items-center justify-between gap-6 px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-150 border border-slate-200 text-xs text-slate-600 transition-all hover:border-slate-300 shadow-xs"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-slate-700 font-medium">Search or jump to...</span>
          </div>
          <div className="flex items-center gap-1 font-mono text-[10px] text-slate-500">
            <span className="kbd-shortcut">⌘K</span>
          </div>
        </button>

        {/* Quick Action: New Research */}
        <button
          onClick={onNewResearch}
          className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all flex items-center gap-1.5"
          title="New Research (Shortcut: N)"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">New Research</span>
          <span className="kbd-shortcut bg-indigo-700/80 border-indigo-400/40 text-white ml-1 hidden lg:inline">N</span>
        </button>

        {/* Quick Action: Upload Document */}
        <button
          onClick={onUploadDocument}
          className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 hover:border-slate-300 text-slate-700 text-xs font-medium transition-all flex items-center gap-1.5 shadow-xs"
          title="Upload Document to Vault"
        >
          <FileUp className="w-3.5 h-3.5 text-slate-500" />
          <span className="hidden sm:inline">Upload</span>
        </button>

        {/* User Profile Menu */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 p-1.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 hover:border-slate-300 transition-all shadow-xs"
            title="User Profile Menu"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-white font-mono text-xs font-bold shadow-xs">
              {getInitials(user?.name, user?.username)}
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          </button>

          {profileOpen && (
            <div className="absolute right-0 mt-2 w-64 rounded-2xl bg-white border border-slate-200 shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-100">
              <div className="px-3 py-2.5 border-b border-slate-100 mb-1">
                <p className="text-xs font-bold text-slate-900 truncate">
                  {user?.name || user?.username || "Authenticated User"}
                </p>
                <p className="text-[11px] text-slate-500 truncate">
                  {user?.email || "user@nexus.internal"}
                </p>
                <div className="flex items-center gap-1.5 mt-2">
                  <span className="text-[9px] font-mono uppercase font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {user?.role || "Researcher"}
                  </span>
                  <span className="text-[9px] font-mono text-slate-400">
                    {user?.tenant_id || "nexus_primary_tenant"}
                  </span>
                </div>
              </div>

              {onViewLanding && (
                <button
                  onClick={() => {
                    setProfileOpen(false);
                    onViewLanding();
                  }}
                  className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-all text-left"
                >
                  <Globe className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Public Landing Page</span>
                </button>
              )}

              <button
                onClick={() => {
                  setProfileOpen(false);
                  logout();
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition-all text-left mt-1"
              >
                <LogOut className="w-3.5 h-3.5 text-rose-500" />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
