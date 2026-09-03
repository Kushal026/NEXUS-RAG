"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  Zap,
  FileText,
  Share2,
  ShieldAlert,
  Sparkles,
  Layers,
  Activity,
  Sliders,
  ArrowRight,
  CornerDownLeft,
  X,
  Plus
} from "lucide-react";

interface CommandItem {
  id: string;
  title: string;
  subtitle: string;
  category: "Navigation" | "Action" | "Intelligence";
  icon: React.ComponentType<{ className?: string }>;
  tabTarget?: "dashboard" | "documents" | "research" | "graph" | "evidence" | "self-correcting" | "multimodal" | "agent" | "evaluation" | "settings";
  action?: () => void;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (tab: "dashboard" | "documents" | "research" | "graph" | "evidence" | "self-correcting" | "multimodal" | "agent" | "evaluation" | "settings") => void;
  onStartResearch?: (query: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNavigate,
  onStartResearch,
}) => {
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const commands: CommandItem[] = [
    {
      id: "research",
      title: "Research & Synthesis",
      subtitle: "Ask inquiries with dual-index retrieval & claim citations",
      category: "Navigation",
      icon: Search,
      tabTarget: "research",
    },
    {
      id: "agent",
      title: "Autonomous Research Agent",
      subtitle: "Multi-stage autonomous planner, gap detector & report compiler",
      category: "Navigation",
      icon: Zap,
      tabTarget: "agent",
    },
    {
      id: "graph",
      title: "Knowledge Graph Traversal",
      subtitle: "Explore extracted entity nodes and typed relations",
      category: "Navigation",
      icon: Share2,
      tabTarget: "graph",
    },
    {
      id: "evidence",
      title: "Evidence & Contradiction Inspector",
      subtitle: "Detect factual disagreement and score source reliability",
      category: "Intelligence",
      icon: ShieldAlert,
      tabTarget: "evidence",
    },
    {
      id: "self-correcting",
      title: "Self-Correction Loop",
      subtitle: "Iterative retrieval retry with query rewriting and verification",
      category: "Intelligence",
      icon: Sparkles,
      tabTarget: "self-correcting",
    },
    {
      id: "multimodal",
      title: "Multimodal Evidence Engine",
      subtitle: "Tables, charts, figures, OCR extracts & structured code",
      category: "Navigation",
      icon: Layers,
      tabTarget: "multimodal",
    },
    {
      id: "documents",
      title: "Knowledge Vault",
      subtitle: "Upload and manage indexed PDF, DOCX, CSV and Markdown files",
      category: "Navigation",
      icon: FileText,
      tabTarget: "documents",
    },
    {
      id: "dashboard",
      title: "Platform Overview",
      subtitle: "Real-time system health, embedding stats and vault metrics",
      category: "Navigation",
      icon: Activity,
      tabTarget: "dashboard",
    },
    {
      id: "evaluation",
      title: "IR Benchmark & Evaluation Suite",
      subtitle: "Recall@K, MRR, NDCG and reasoning benchmark metrics",
      category: "Intelligence",
      icon: Activity,
      tabTarget: "evaluation",
    },
    {
      id: "settings",
      title: "Model & Platform Settings",
      subtitle: "Configure embedding models, rerankers, and retrieval weights",
      category: "Navigation",
      icon: Sliders,
      tabTarget: "settings",
    },
  ];

  const filteredCommands = commands.filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.subtitle.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setSearch("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [search]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.max(1, filteredCommands.length));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) =>
        prev === 0 ? Math.max(0, filteredCommands.length - 1) : prev - 1
      );
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        executeCommand(filteredCommands[selectedIndex]);
      } else if (search.trim() && onStartResearch) {
        onStartResearch(search.trim());
        onClose();
      }
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  const executeCommand = (item: CommandItem) => {
    if (item.tabTarget) {
      onNavigate(item.tabTarget);
    }
    if (item.action) {
      item.action();
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-150">
      <div
        className="w-full max-w-2xl bg-[#0d1117] border border-slate-800/90 rounded-2xl shadow-2xl shadow-black/80 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-800/80 bg-slate-900/50">
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or research inquiry..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          {search ? (
            <button
              onClick={() => setSearch("")}
              className="p-1 rounded text-slate-400 hover:text-slate-200"
            >
              <X className="w-4 h-4" />
            </button>
          ) : (
            <div className="flex items-center gap-1 text-[10px] text-slate-500 font-mono">
              <span className="kbd-shortcut">ESC</span>
            </div>
          )}
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 divide-y divide-slate-800/40">
          {filteredCommands.length === 0 ? (
            search.trim() ? (
              <div
                onClick={() => {
                  if (onStartResearch) {
                    onStartResearch(search.trim());
                    onClose();
                  }
                }}
                className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-indigo-300 text-xs flex items-center justify-between cursor-pointer hover:bg-indigo-900/30 transition-all"
              >
                <div className="flex items-center gap-2.5">
                  <Search className="w-4 h-4 text-indigo-400" />
                  <span>
                    Execute research query for <strong className="text-white font-semibold">"{search}"</strong>
                  </span>
                </div>
                <div className="flex items-center gap-1 font-mono text-[10px] text-indigo-400">
                  <span>Enter</span>
                  <CornerDownLeft className="w-3.5 h-3.5" />
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-500">
                No matching commands found.
              </div>
            )
          ) : (
            filteredCommands.map((cmd, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = cmd.icon;
              return (
                <div
                  key={cmd.id}
                  onClick={() => executeCommand(cmd)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? "bg-slate-800/90 text-white shadow-sm border border-slate-700/60"
                      : "text-slate-300 hover:bg-slate-850/50"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`p-2 rounded-lg ${
                        isSelected
                          ? "bg-indigo-500/20 text-indigo-300"
                          : "bg-slate-900 text-slate-400 border border-slate-800"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-100 truncate">
                        {cmd.title}
                      </p>
                      <p className="text-[11px] text-slate-400 truncate">
                        {cmd.subtitle}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[10px] font-mono text-slate-500 uppercase px-2 py-0.5 rounded bg-slate-900/80 border border-slate-800">
                      {cmd.category}
                    </span>
                    {isSelected && (
                      <CornerDownLeft className="w-3.5 h-3.5 text-indigo-400" />
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="px-4 py-2.5 bg-slate-950/90 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="kbd-shortcut">↑</span>
              <span className="kbd-shortcut">↓</span>
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <span className="kbd-shortcut">↵</span>
              Select
            </span>
          </div>
          <div className="flex items-center gap-1 font-mono text-[10px] text-slate-400">
            <span>NEXUS Quick Switcher</span>
          </div>
        </div>
      </div>
    </div>
  );
};
