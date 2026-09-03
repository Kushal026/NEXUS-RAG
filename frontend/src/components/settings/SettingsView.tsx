"use client";

import React, { useState } from "react";
import {
  Sliders,
  Database,
  Cpu,
  Layers,
  Save,
  CheckCircle2,
  Server,
  Zap,
  ShieldAlert
} from "lucide-react";
import { SystemStatus, AppSettings } from "../../types";

interface SettingsViewProps {
  status: SystemStatus | null;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ status }) => {
  const [settings, setSettings] = useState<AppSettings>({
    llmProvider: status?.llm_provider || "local_heuristic",
    llmModel: "gpt-4o-mini",
    embeddingProvider: status?.embedding_provider || "sentence_transformers",
    embeddingModel: "all-MiniLM-L6-v2",
    rerankerProvider: status?.reranker_provider || "cross_encoder",
    chunkSize: 600,
    chunkOverlap: 120,
    defaultTopK: 10,
  });

  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-indigo-400" />
            System & Pipeline Configuration
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure semantic chunking parameters, neural embeddings, reranker models, and pluggable LLM synthesis backends.
          </p>
        </div>
        {saved && (
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" /> Settings Saved
          </span>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Semantic Chunking Configuration */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            Semantic Chunking Parameters
          </h3>
          <p className="text-xs text-slate-400">
            Governs how incoming PDF, DOCX, Markdown, and TXT files are split into contextual windows with boundary preservation.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-slate-300">
                <span>Target Chunk Size (Characters)</span>
                <span className="font-mono text-cyan-400 font-bold">{settings.chunkSize}</span>
              </div>
              <input
                type="range"
                min="200"
                max="2000"
                step="50"
                value={settings.chunkSize}
                onChange={(e) => setSettings({ ...settings, chunkSize: parseInt(e.target.value) })}
                className="w-full accent-cyan-500"
              />
              <span className="text-[10px] text-slate-500">Recommended: 500-800 chars for dense passage retrieval.</span>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-slate-300">
                <span>Chunk Overlap (Characters)</span>
                <span className="font-mono text-indigo-400 font-bold">{settings.chunkOverlap}</span>
              </div>
              <input
                type="range"
                min="20"
                max="400"
                step="20"
                value={settings.chunkOverlap}
                onChange={(e) => setSettings({ ...settings, chunkOverlap: parseInt(e.target.value) })}
                className="w-full accent-indigo-500"
              />
              <span className="text-[10px] text-slate-500">Ensures sentence context is not truncated across chunk boundaries.</span>
            </div>
          </div>
        </div>

        {/* AI & Embeddings Model Setup */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            AI Models & Vector Store Providers
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
            <div className="space-y-2">
              <label className="text-slate-300 font-medium">Embedding Engine</label>
              <select
                value={settings.embeddingProvider}
                onChange={(e) => setSettings({ ...settings, embeddingProvider: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="sentence_transformers">SentenceTransformers (all-MiniLM-L6-v2) - Local</option>
                <option value="openai">OpenAI (text-embedding-3-small) - Cloud</option>
                <option value="hash_mock">Deterministic FastEmbed / Mock - Offline</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-slate-300 font-medium">LLM Synthesis Provider</label>
              <select
                value={settings.llmProvider}
                onChange={(e) => setSettings({ ...settings, llmProvider: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="local_heuristic">Deterministic Heuristic Synthesizer (Zero API Keys)</option>
                <option value="openai">OpenAI (GPT-4o-mini / GPT-4o)</option>
                <option value="anthropic">Anthropic Claude</option>
                <option value="ollama">Ollama (Local LLM)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-slate-300 font-medium">Cross-Encoder Neural Reranker</label>
              <select
                value={settings.rerankerProvider}
                onChange={(e) => setSettings({ ...settings, rerankerProvider: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="cross_encoder">ms-marco-MiniLM-L-6-v2 (Cross-Encoder Neural)</option>
                <option value="heuristic">Heuristic Lexical Overlap</option>
                <option value="none">Disabled (Direct RRF Only)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-slate-300 font-medium">Database Layer (Vector DB)</label>
              <div className="px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300 flex items-center justify-between">
                <span>PostgreSQL 16 + pgvector</span>
                <span className="text-[11px] font-mono text-emerald-400 font-bold">Enabled</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Configuration Changes
          </button>
        </div>
      </form>
    </div>
  );
};
