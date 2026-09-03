"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  ShieldCheck,
  Search,
  Zap,
  Share2,
  Clock,
  ShieldAlert,
  Sparkles,
  Layers,
  ArrowRight,
  Database,
  Cpu,
  CheckCircle2,
  FileText,
  Activity,
  GitBranch,
  Lock,
  ChevronRight,
  ExternalLink,
  BookOpen,
  Filter,
  BarChart2
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

interface LandingPageProps {
  onStartResearch: () => void;
  onOpenAuth: (mode?: "signin" | "signup") => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartResearch,
  onOpenAuth,
}) => {
  const { isAuthenticated, user } = useAuth();
  const [activePipelineStep, setActivePipelineStep] = useState(0);

  const capabilities = [
    {
      title: "Hybrid Retrieval",
      description: "Dense Cosine vectors + Sparse BM25 Okapi search unified with Reciprocal Rank Fusion & Cross-Encoder reranking.",
      icon: Database,
      badge: "Dense + Sparse",
      gradient: "from-indigo-500/10 via-indigo-500/5 to-transparent",
      accent: "text-indigo-600",
      border: "hover:border-indigo-400",
    },
    {
      title: "Temporal Intelligence",
      description: "Understand knowledge across time, resolve superseded specifications, and isolate temporal version diffs.",
      icon: Clock,
      badge: "Time-Travel RAG",
      gradient: "from-amber-500/10 via-amber-500/5 to-transparent",
      accent: "text-amber-600",
      border: "hover:border-amber-400",
    },
    {
      title: "Knowledge Graph Traversal",
      description: "Entity resolution, typed directional relationships, and sub-graph context expansion with strict provenance.",
      icon: Share2,
      badge: "Neo4j & Graph RAG",
      gradient: "from-cyan-500/10 via-cyan-500/5 to-transparent",
      accent: "text-cyan-600",
      border: "hover:border-cyan-400",
    },
    {
      title: "Contradiction Detection",
      description: "NLI-based factual disagreement analysis identifying conflicts between papers, datasets, and condition changes.",
      icon: ShieldAlert,
      badge: "NLI Contradiction Engine",
      gradient: "from-emerald-500/10 via-emerald-500/5 to-transparent",
      accent: "text-emerald-600",
      border: "hover:border-emerald-400",
    },
    {
      title: "Evidence Verification",
      description: "Evaluate evidence sufficiency, calibrate multi-factor confidence, and prevent hallucinations before synthesis.",
      icon: CheckCircle2,
      badge: "Zero-Hallucination",
      gradient: "from-blue-500/10 via-blue-500/5 to-transparent",
      accent: "text-blue-600",
      border: "hover:border-blue-400",
    },
    {
      title: "Self-Correcting Retrieval",
      description: "Iterative recovery loop with missing-aspect query rewriting, evidence accumulation, and answer verification.",
      icon: Sparkles,
      badge: "Iterative Loop",
      gradient: "from-yellow-500/10 via-yellow-500/5 to-transparent",
      accent: "text-yellow-600",
      border: "hover:border-yellow-400",
    },
    {
      title: "Multimodal Evidence",
      description: "Cross-modality retrieval across structured tables, charts, axes/values, OCR scans, code, and text passages.",
      icon: Layers,
      badge: "Tables, Charts, OCR",
      gradient: "from-violet-500/10 via-violet-500/5 to-transparent",
      accent: "text-violet-600",
      border: "hover:border-violet-400",
    },
    {
      title: "Autonomous Research Agent",
      description: "Multi-stage goal planner, gap detector, and synthesizer compiling 9-section comprehensive academic research reports.",
      icon: Zap,
      badge: "9-Section Report Agent",
      gradient: "from-rose-500/10 via-rose-500/5 to-transparent",
      accent: "text-rose-600",
      border: "hover:border-rose-400",
    },
  ];

  const pipelineStages = [
    {
      name: "UNDERSTAND",
      label: "Query Understanding",
      desc: "Decompose complex questions into atomic search aspects, temporal filters, and entity anchors.",
      icon: Search,
    },
    {
      name: "RETRIEVE",
      label: "Hybrid Dual-Index Search",
      desc: "Simultaneously query 384-dimensional dense semantic vectors and lexical BM25 token indices.",
      icon: Database,
    },
    {
      name: "RERANK",
      label: "Cross-Encoder Scoring",
      desc: "Compute exact cross-attention relevance scores for top candidate pools via ms-marco.",
      icon: Zap,
    },
    {
      name: "CONNECT",
      label: "Knowledge Graph Traversal",
      desc: "Expand retrieved facts with 2-hop entity relations, typed links, and document citations.",
      icon: Share2,
    },
    {
      name: "COMPARE",
      label: "Contradiction & NLI Analysis",
      desc: "Perform pairwise NLI entailment checks to detect conflicting claims across disparate sources.",
      icon: ShieldAlert,
    },
    {
      name: "VERIFY",
      label: "Sufficiency & Coverage Check",
      desc: "Confirm that accumulated evidence answers all sub-inquiries before generating conclusions.",
      icon: CheckCircle2,
    },
    {
      name: "REASON",
      label: "Evidence Synthesis",
      desc: "Synthesize structured findings with strict boundary isolation against prompt injection.",
      icon: Cpu,
    },
    {
      name: "CITE",
      label: "Claim-Level Provenance",
      desc: "Attribute every single claim to exact document names, pages, and verifiable quotes.",
      icon: FileText,
    },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans selection:bg-indigo-500/20 selection:text-indigo-800 overflow-x-hidden">
      {/* Top Public Navigation Bar */}
      <header className="sticky top-0 z-40 border-b border-slate-200/90 bg-white/85 backdrop-blur-xl px-6 py-3.5 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-md shadow-indigo-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-extrabold tracking-tight text-slate-900 leading-none">NEXUS</h1>
            <p className="text-[10px] text-slate-500 font-medium">Evidence Intelligence for AI</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-xs text-slate-600">
          <a href="#capabilities" className="hover:text-slate-900 transition-colors font-medium">
            Capabilities
          </a>
          <a href="#pipeline" className="hover:text-slate-900 transition-colors font-medium">
            How It Works
          </a>
          <a href="#trust" className="hover:text-slate-900 transition-colors font-medium">
            Trust & Provenance
          </a>
        </nav>

        {/* User CTA */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <button
              onClick={onStartResearch}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all flex items-center gap-2"
            >
              <span>Open Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <>
              <button
                onClick={() => onOpenAuth("signin")}
                className="px-3.5 py-2 rounded-xl text-xs font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-all"
              >
                Sign In
              </button>
              <button
                onClick={() => onOpenAuth("signup")}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all flex items-center gap-1.5"
              >
                <span>Get Started</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 px-6 max-w-7xl mx-auto text-center space-y-8">
        {/* Subtle Ambient Radial Glows */}
        <div className="absolute left-1/2 -top-24 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-indigo-200/40 via-cyan-100/30 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="space-y-4 max-w-3xl mx-auto relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Next-Generation Neural Evidence Engine</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1]">
            Evidence Intelligence <br />
            <span className="bg-gradient-to-r from-indigo-600 via-cyan-600 to-indigo-700 bg-clip-text text-transparent">
              for Enterprise AI
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Retrieve, connect, verify, and reason over complex information with evidence-backed AI. Moving beyond naive chunk search into verifiable truth.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 relative z-10 pt-2">
          <button
            onClick={onStartResearch}
            className="px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-xl shadow-indigo-600/20 transition-all flex items-center gap-2"
          >
            <span>Start Research</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <a
            href="#capabilities"
            className="px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-sm font-medium transition-all shadow-xs"
          >
            Explore NEXUS
          </a>
        </div>

        {/* Interactive Subtle Engine Flow Visualization */}
        <div className="pt-8 relative z-10 max-w-4xl mx-auto">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-200/90 shadow-lg relative overflow-hidden bg-white/95">
            <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-100 text-xs text-slate-500">
              <span className="font-mono text-indigo-600 uppercase tracking-wider font-semibold">
                Evidence Engine Flow Visualizer
              </span>
              <span>Interactive Pipeline</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-indigo-600 font-bold">STAGE 01</span>
                  <Database className="w-4 h-4 text-indigo-600" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">Hybrid Retrieval</h4>
                <p className="text-[11px] text-slate-500">pgvector + BM25 Okapi</p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-cyan-600 font-bold">STAGE 02</span>
                  <Share2 className="w-4 h-4 text-cyan-600" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">Graph Expansion</h4>
                <p className="text-[11px] text-slate-500">2-Hop Entity Traversal</p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-emerald-600 font-bold">STAGE 03</span>
                  <ShieldAlert className="w-4 h-4 text-emerald-600" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">NLI Contradictions</h4>
                <p className="text-[11px] text-slate-500">Pairwise Entailment</p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-rose-600 font-bold">STAGE 04</span>
                  <FileText className="w-4 h-4 text-rose-600" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">Attributed Synthesis</h4>
                <p className="text-[11px] text-slate-500">Claim-Level Citations</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Product Capabilities Bento Grid */}
      <section id="capabilities" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-xs uppercase font-mono font-bold tracking-wider text-indigo-600">
            System Capabilities
          </h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Engineered for Grounded, Verifiable Research
          </h3>
          <p className="text-xs sm:text-sm text-slate-600">
            Eight interconnected neural intelligence engines designed to turn multi-format document collections into verified, explainable knowledge.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {capabilities.map((cap, idx) => {
            const Icon = cap.icon;
            return (
              <div
                key={idx}
                className={`glass-panel p-6 rounded-2xl border border-slate-200/90 ${cap.border} transition-all duration-300 space-y-4 relative overflow-hidden group bg-white hover:shadow-md`}
              >
                <div
                  className={`absolute inset-0 bg-gradient-to-b ${cap.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none`}
                />

                <div className="relative z-10 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className={`p-2.5 rounded-xl bg-slate-50 border border-slate-200 ${cap.accent}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-600">
                      {cap.badge}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900">{cap.title}</h4>
                  <p className="text-xs text-slate-600 leading-relaxed">{cap.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* How NEXUS Works Interactive Pipeline */}
      <section id="pipeline" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-xs uppercase font-mono font-bold tracking-wider text-cyan-600">
            Execution Pipeline
          </h2>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            How NEXUS Verifies Truth
          </h3>
          <p className="text-xs sm:text-sm text-slate-600">
            From natural language inquiry to grounded report in eight deterministic verification stages.
          </p>
        </div>

        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-200/90 space-y-8 bg-white">
          {/* Horizontal Step Buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
            {pipelineStages.map((stage, sIdx) => (
              <button
                key={sIdx}
                onClick={() => setActivePipelineStep(sIdx)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  activePipelineStep === sIdx
                    ? "bg-indigo-50 border-indigo-300 text-indigo-900 shadow-xs"
                    : "bg-slate-50/70 border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <div className="text-[10px] font-mono text-indigo-600 font-bold mb-1">
                  0{sIdx + 1}
                </div>
                <div className="text-xs font-bold truncate">{stage.name}</div>
              </button>
            ))}
          </div>

          {/* Active Step Showcase */}
          <div className="p-6 rounded-2xl bg-slate-50/90 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <span className="text-[10px] font-mono uppercase font-bold text-indigo-700 px-2 py-0.5 rounded bg-indigo-100 border border-indigo-200">
                Step 0{activePipelineStep + 1} of 08
              </span>
              <h4 className="text-lg font-bold text-slate-900">
                {pipelineStages[activePipelineStep].label}
              </h4>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                {pipelineStages[activePipelineStep].desc}
              </p>
            </div>

            <button
              onClick={() => setActivePipelineStep((prev) => (prev + 1) % pipelineStages.length)}
              className="px-4 py-2.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-all flex items-center gap-2 shrink-0 self-start md:self-center shadow-xs"
            >
              <span>Next Stage</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {/* Trust & Evidence Transparency Section */}
      <section id="trust" className="py-20 px-6 max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-6 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Evidence Transparency</span>
            </div>

            <h3 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
              Don't just get an answer. <br />
              <span className="text-emerald-600">Understand why it can be trusted.</span>
            </h3>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Standard language models hallucinate plausible-sounding falsehoods. NEXUS forces every token through a multi-factor verification pipeline with exact page provenance and conflict awareness.
            </p>

            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <strong className="text-slate-900">Claim-Level Superscript Citations:</strong> Every assertion maps to an exact document excerpt quote and page number.
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <strong className="text-slate-900">Factual Contradiction Alerts:</strong> Conflicting benchmarks or outdated operating limits are highlighted rather than averaged away.
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div className="text-xs">
                  <strong className="text-slate-900">Boundary-Isolated Prompt Defense:</strong> Untrusted retrieved documents cannot inject instructions into system prompts.
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-6">
            <div className="glass-panel p-6 rounded-3xl border border-slate-200/90 space-y-4 bg-white shadow-md">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="text-xs font-bold text-slate-900">Attributed Research Output</span>
                <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-semibold">
                  98.4% Confidence
                </span>
              </div>

              <blockquote className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed space-y-2">
                <p>
                  "The quantum cryogenic controller operating boundary was upgraded in 2026 to <strong className="text-slate-900 font-semibold">12.5 mK</strong>, superseding the legacy 2024 specification of 18.0 mK."
                </p>
                <div className="pt-2 flex flex-wrap gap-2 text-[10px] font-mono">
                  <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                    [1] Q-Controller-2026.pdf • P.14
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                    ⚠ Replaces 2024 Spec
                  </span>
                </div>
              </blockquote>
            </div>
          </div>
        </div>
      </section>

      {/* Public Footer */}
      <footer className="border-t border-slate-200/80 bg-white py-6 px-6 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-indigo-600 flex items-center justify-center text-white">
            <ShieldCheck className="w-3.5 h-3.5" />
          </div>
          <span className="font-bold text-slate-900">NEXUS</span>
          <span>•</span>
          <span>Evidence Intelligence for AI</span>
        </div>

        <div className="flex items-center gap-6 text-[11px] text-slate-500">
          <span>Enterprise Security</span>
          <span>•</span>
          <span>Multi-Tenant Isolation</span>
          <span>•</span>
          <span>MIT License</span>
        </div>
      </footer>
    </div>
  );
};
