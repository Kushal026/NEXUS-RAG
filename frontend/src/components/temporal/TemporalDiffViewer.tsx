"use client";

import React from "react";
import {
  GitCompare,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  Activity,
  Calendar
} from "lucide-react";
import { TemporalDiffResult } from "../../types";

interface TemporalDiffViewerProps {
  diffResult: TemporalDiffResult;
}

export const TemporalDiffViewer: React.FC<TemporalDiffViewerProps> = ({ diffResult }) => {
  return (
    <div className="glass-panel p-6 rounded-2xl border border-cyan-500/30 space-y-4">
      {/* Diff Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <GitCompare className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">
              Temporal Evolution & Version Diff: {diffResult.topic}
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            {diffResult.diff_summary}
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            {diffResult.period_from}
          </span>
          <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
          <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            {diffResult.period_to}
          </span>
        </div>
      </div>

      {/* Detected Changes Cards */}
      <div className="space-y-3">
        {diffResult.detected_changes.length > 0 ? (
          diffResult.detected_changes.map((change, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-950/80 border border-slate-850 space-y-3 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-cyan-400" />
                  {change.attribute}
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                  {change.change_type}
                </span>
              </div>

              {/* Side by side state evolution */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase">
                    Prior State ({change.prior_date})
                  </span>
                  <p className="text-rose-300 font-semibold">{change.prior_state}</p>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-emerald-500/30 space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase">
                    Current State ({change.current_date})
                  </span>
                  <p className="text-emerald-300 font-semibold">{change.current_state}</p>
                </div>
              </div>

              <p className="text-slate-400 text-[11px] leading-relaxed font-sans">
                {change.explanation}
              </p>
            </div>
          ))
        ) : (
          <div className="p-6 text-center text-slate-500 text-xs font-mono">
            No specification changes detected between {diffResult.period_from} and {diffResult.period_to}.
          </div>
        )}
      </div>
    </div>
  );
};
