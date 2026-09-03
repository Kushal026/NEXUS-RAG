"use client";

import React from "react";
import {
  Clock,
  Calendar,
  History,
  Sparkles,
  CheckCircle2,
  ChevronRight,
  Filter,
  ShieldCheck,
  RotateCcw
} from "lucide-react";
import { TemporalFilter } from "../../types";

interface TemporalTimelineBarProps {
  temporalFilter: TemporalFilter;
  onChange: (filter: TemporalFilter) => void;
}

export const TemporalTimelineBar: React.FC<TemporalTimelineBarProps> = ({
  temporalFilter,
  onChange,
}) => {
  const quickEpochs = [
    { label: "Latest Only", latest_only: true, as_of: undefined },
    { label: "All Epochs", latest_only: false, as_of: undefined },
    { label: "As of 2023", latest_only: false, as_of: "2023" },
    { label: "As of 2024", latest_only: false, as_of: "2024" },
    { label: "As of 2026", latest_only: false, as_of: "2026" },
  ];

  return (
    <div className="p-3.5 rounded-xl bg-slate-950/80 border border-indigo-500/20 flex flex-wrap items-center justify-between gap-3 text-xs">
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <Clock className="w-4 h-4" />
        </div>
        <div>
          <span className="font-semibold text-slate-200 flex items-center gap-1.5">
            Temporal Time-Travel Control
            {temporalFilter.as_of_date && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">
                Epoch: {temporalFilter.as_of_date}
              </span>
            )}
            {temporalFilter.latest_only && (
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono border border-emerald-500/30">
                Latest Only
              </span>
            )}
          </span>
          <p className="text-[11px] text-slate-400">
            Filter evidence by historical point-in-time state or restrict to current active version.
          </p>
        </div>
      </div>

      {/* Epoch Presets */}
      <div className="flex flex-wrap items-center gap-1.5">
        {quickEpochs.map((ep, idx) => {
          const isActive =
            (ep.latest_only && temporalFilter.latest_only) ||
            (!ep.latest_only && !temporalFilter.latest_only && temporalFilter.as_of_date === ep.as_of);

          return (
            <button
              key={idx}
              type="button"
              onClick={() =>
                onChange({
                  ...temporalFilter,
                  latest_only: ep.latest_only,
                  as_of_date: ep.as_of,
                })
              }
              className={`px-3 py-1.5 rounded-lg font-mono text-[11px] transition-all flex items-center gap-1 ${
                isActive
                  ? "bg-indigo-600 text-white font-bold shadow-md shadow-indigo-600/30 border border-indigo-400"
                  : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-850"
              }`}
            >
              {ep.label}
            </button>
          );
        })}

        {(temporalFilter.as_of_date || temporalFilter.latest_only) && (
          <button
            type="button"
            onClick={() =>
              onChange({
                latest_only: false,
                as_of_date: undefined,
                start_date: undefined,
                end_date: undefined,
              })
            }
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 text-[11px]"
            title="Reset Time Filter"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
