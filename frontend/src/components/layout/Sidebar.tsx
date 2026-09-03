"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Search,
  Zap,
  Sparkles,
  FileText,
  Share2,
  Layers,
  ShieldAlert,
  Activity,
  Sliders,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Database,
  Cpu,
  Server
} from "lucide-react";
import { SystemStatus } from "../../types";

export type TabKey =
  | "dashboard"
  | "documents"
  | "research"
  | "graph"
  | "evidence"
  | "self-correcting"
  | "multimodal"
  | "agent"
  | "evaluation"
  | "settings";

interface SidebarProps {
  activeTab: TabKey;
  setActiveTab: (tab: TabKey) => void;
  status: SystemStatus | null;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  onOpenCommandPalette: () => void;
}

interface NavItem {
  id: TabKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
  badgeColor?: string;
  gradient?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  status,
  collapsed,
  setCollapsed,
  onOpenCommandPalette,
}) => {
  const navSections: { title: string; items: NavItem[] }[] = [
    {
      title: "Research",
      items: [
        {
          id: "research",
          label: "Research / Ask",
          icon: Search,
        },
        {
          id: "agent",
          label: "Autonomous Agent",
          icon: Zap,
          badge: "Auto",
          badgeColor: "bg-rose-50 text-rose-600 border-rose-200",
        },
        {
          id: "self-correcting",
          label: "Self-Correction",
          icon: Sparkles,
        },
      ],
    },
    {
      title: "Knowledge",
      items: [
        {
          id: "documents",
          label: "Document Vault",
          icon: FileText,
          badge: status ? status.total_documents : undefined,
          badgeColor: "bg-slate-100 text-slate-700 border-slate-200",
        },
        {
          id: "graph",
          label: "Knowledge Graph",
          icon: Share2,
        },
        {
          id: "multimodal",
          label: "Multimodal Engine",
          icon: Layers,
        },
      ],
    },
    {
      title: "Intelligence",
      items: [
        {
          id: "evidence",
          label: "Evidence Inspector",
          icon: ShieldAlert,
        },
        {
          id: "evaluation",
          label: "IR Benchmarks",
          icon: Activity,
        },
      ],
    },
    {
      title: "Platform",
      items: [
        {
          id: "dashboard",
          label: "Overview",
          icon: Activity,
        },
        {
          id: "settings",
          label: "Settings",
          icon: Sliders,
        },
      ],
    },
  ];

  return (
    <aside
      className={`relative flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-200/90 bg-[#ffffff] transition-all duration-300 select-none z-30 shadow-sm ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-slate-200/80 h-16">
        <div
          onClick={() => setActiveTab("dashboard")}
          className="flex items-center gap-3 cursor-pointer min-w-0"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-md shadow-indigo-500/25 shrink-0">
            <ShieldCheck className="w-4.5 h-4.5 text-white" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <h1 className="text-base font-extrabold tracking-tight text-slate-900 leading-none">
                NEXUS
              </h1>
              <p className="text-[10px] text-slate-500 font-medium truncate mt-0.5">
                Evidence Intelligence
              </p>
            </div>
          )}
        </div>

        {/* Collapse button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 border border-transparent hover:border-slate-200 transition-all"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Quick Search / Command Palette trigger */}
      <div className="p-3 border-b border-slate-200/80">
        <button
          onClick={onOpenCommandPalette}
          className={`w-full flex items-center justify-between rounded-xl bg-slate-100/80 hover:bg-slate-100 border border-slate-200 text-slate-600 text-xs transition-all ${
            collapsed ? "p-2 justify-center" : "px-3 py-2"
          }`}
          title="Command Menu (⌘K)"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-500" />
            {!collapsed && <span className="font-medium text-slate-700">Quick Search</span>}
          </div>
          {!collapsed && (
            <div className="flex items-center gap-1 font-mono text-[10px] text-slate-500">
              <span className="kbd-shortcut">⌘K</span>
            </div>
          )}
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-5">
        {navSections.map((section, sIdx) => (
          <div key={sIdx} className="space-y-1">
            {!collapsed && (
              <h3 className="px-2.5 text-[10px] uppercase font-bold tracking-wider text-slate-400 font-mono">
                {section.title}
              </h3>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const isActive = activeTab === item.id;
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`group relative w-full flex items-center rounded-xl text-xs font-medium transition-all ${
                      collapsed ? "p-2.5 justify-center" : "px-3 py-2 justify-between"
                    } ${
                      isActive
                        ? "text-indigo-700 bg-indigo-50/90 border border-indigo-100 shadow-xs font-semibold"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/70 border border-transparent"
                    }`}
                    title={collapsed ? item.label : undefined}
                  >
                    {/* Active Indicator Bar */}
                    {isActive && (
                      <motion.div
                        layoutId="activeSidebarIndicator"
                        className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-indigo-600 shadow-xs"
                        transition={{ type: "spring", stiffness: 350, damping: 30 }}
                      />
                    )}

                    <div className="flex items-center gap-2.5 min-w-0">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          isActive
                            ? "text-indigo-600"
                            : "text-slate-500 group-hover:text-slate-800"
                        }`}
                      />
                      {!collapsed && (
                        <span className="truncate">{item.label}</span>
                      )}
                    </div>

                    {!collapsed && item.badge !== undefined && (
                      <span
                        className={`text-[10px] font-mono font-semibold px-2 py-0.2 rounded-full border ${
                          item.badgeColor || "bg-slate-100 text-slate-600 border-slate-200"
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer System Telemetry */}
      <div className="p-3 border-t border-slate-200/80 bg-slate-50/70">
        {!collapsed ? (
          <div className="flex items-center justify-between text-[11px] text-slate-600">
            <div className="flex items-center gap-2 min-w-0">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0" />
              <div className="truncate">
                <p className="font-semibold text-slate-900 leading-none">FastAPI Core</p>
                <p className="text-[10px] text-slate-500 font-mono mt-0.5 truncate">
                  {status?.embedding_provider || "Dense + BM25"}
                </p>
              </div>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white border border-slate-200 text-emerald-600 font-semibold shadow-xs">
              Online
            </span>
          </div>
        ) : (
          <div className="flex justify-center" title="System Online">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>
        )}
      </div>
    </aside>
  );
};
