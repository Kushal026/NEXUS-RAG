"use client";

import React from "react";
import { ShieldCheck, Cpu, Database, Layers, FileText, Search, Activity, Zap, Share2 } from "lucide-react";
import { SystemStatus } from "../../types";

interface NavbarProps {
  status: SystemStatus | null;
  activeTab: "dashboard" | "documents" | "research" | "graph" | "evaluation" | "settings";
  setActiveTab: (tab: "dashboard" | "documents" | "research" | "graph" | "evaluation" | "settings") => void;
}

export const Navbar: React.FC<NavbarProps> = ({ status, activeTab, setActiveTab }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
      {/* Brand */}
      <div
        onClick={() => setActiveTab("dashboard")}
        className="flex items-center gap-3 cursor-pointer"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-white">NEXUS-RAG</h1>
            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Phase 5 Graph Engine
            </span>
          </div>
          <p className="text-xs text-slate-400">Neural Evidence & eXplainability Unified Search</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center bg-slate-950/80 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => setActiveTab("dashboard")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === "dashboard"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Activity className="w-4 h-4" />
          Dashboard
        </button>

        <button
          onClick={() => setActiveTab("documents")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === "documents"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <FileText className="w-4 h-4" />
          Documents
          {status && (
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] text-slate-300">
              {status.total_documents}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("research")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === "research"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Search className="w-4 h-4" />
          Research / Ask
        </button>

        <button
          onClick={() => setActiveTab("graph")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === "graph"
              ? "bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-md shadow-cyan-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Share2 className="w-4 h-4 text-cyan-400" />
          Knowledge Graph
          <span className="ml-0.5 px-1.5 py-0.2 rounded-full bg-cyan-500/20 text-[9px] text-cyan-300 font-semibold uppercase">
            Phase 5
          </span>
        </button>

        <button
          onClick={() => setActiveTab("evaluation")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === "evaluation"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Zap className="w-4 h-4" />
          Evaluation & IR
        </button>

        <button
          onClick={() => setActiveTab("settings")}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === "settings"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Layers className="w-4 h-4" />
          Settings
        </button>
      </div>

      {/* Engine Status Indicators */}
      <div className="hidden lg:flex items-center gap-4 text-xs">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-slate-300">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">LLM:</span>
          <span className="font-mono text-[11px] text-slate-200">{status?.llm_provider || "heuristic"}</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-slate-300">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-400">Embed:</span>
          <span className="font-mono text-[11px] text-slate-200">{status?.embedding_provider || "sentence_transformers"}</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-slate-300">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-400">Chunks:</span>
          <span className="font-mono font-semibold text-emerald-400">{status?.total_chunks || 0}</span>
        </div>
      </div>
    </header>
  );
};
