"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Search,
  Sparkles,
  Scale,
  Cpu,
  Layers,
  ArrowRight,
  Info,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  BookOpen,
  Zap,
  HelpCircle,
  Clock,
  Award
} from "lucide-react";
import {
  EvidenceIntelligenceReport,
  GroupedClaimEvidence,
  NLIResult,
  NLIClassificationType,
  DocumentInfo
} from "../../types";
import { api } from "../../services/api";

interface EvidenceInspectorProps {
  documents?: DocumentInfo[];
}

export const EvidenceInspector: React.FC<EvidenceInspectorProps> = ({ documents = [] }) => {
  const [query, setQuery] = useState("What is the accuracy and evaluation performance of Transformer models?");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<EvidenceIntelligenceReport | null>(null);
  const [selectedClaim, setSelectedClaim] = useState<GroupedClaimEvidence | null>(null);

  // NLI Sandbox State
  const [premise, setPremise] = useState("Model accuracy is 91% on the GLUE benchmark.");
  const [hypothesis, setHypothesis] = useState("Model accuracy is 87% on the SQuAD benchmark.");
  const [nliResult, setNliResult] = useState<NLIResult | null>(null);
  const [nliLoading, setNliLoading] = useState(false);

  // Preset NLI Examples
  const nliPresets = [
    {
      title: "Direct Contradiction",
      p: "Model accuracy is 91% on test data.",
      h: "Model accuracy is 87% on test data.",
    },
    {
      title: "Different Conditions",
      p: "Model achieved 91% accuracy on the GLUE benchmark.",
      h: "Model achieved 87% accuracy on the SQuAD dataset.",
    },
    {
      title: "Temporal Difference",
      p: "In 2022, model accuracy was 85%.",
      h: "In 2024, model accuracy was upgraded to 93%.",
    },
    {
      title: "Mutual Entailment",
      p: "The Transformer architecture utilizes the self-attention mechanism.",
      h: "Self-attention mechanism is the foundation of Transformer models.",
    },
  ];

  const handleAnalyze = async () => {
    if (!query.trim()) return;
    try {
      setLoading(true);
      const res = await api.analyzeEvidence(query, { top_k: 8 });
      setReport(res);
      if (res.grouped_claims.length > 0) {
        setSelectedClaim(res.grouped_claims[0]);
      }
    } catch (err) {
      console.error("Evidence analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunNLI = async () => {
    if (!premise.trim() || !hypothesis.trim()) return;
    try {
      setNliLoading(true);
      const res = await api.evaluateNLI(premise, hypothesis);
      setNliResult(res);
    } catch (err) {
      console.error("NLI test failed:", err);
    } finally {
      setNliLoading(false);
    }
  };

  const getNliVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case "entailment":
        return (
          <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> Entailment (Agreement)
          </span>
        );
      case "contradiction":
        return (
          <span className="px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-bold flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Direct Contradiction
          </span>
        );
      case "different_conditions":
        return (
          <span className="px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-bold flex items-center gap-1.5">
            <Scale className="w-3.5 h-3.5" /> Different Conditions / Datasets
          </span>
        );
      case "temporal_difference":
        return (
          <span className="px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-bold flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" /> Temporal Evolution
          </span>
        );
      case "partial_contradiction":
        return (
          <span className="px-2.5 py-1 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20 text-xs font-bold flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Partial Contradiction
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700 text-xs font-bold">
            Neutral / Unrelated
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden shadow-xl shadow-emerald-950/20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-emerald-600/10 via-teal-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/25">
                <ShieldAlert className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  Evidence Intelligence Engine
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Phase 6 Active
                  </span>
                </h2>
                <p className="text-xs text-slate-400">
                  Zero-hallucination evidence analysis: Contradiction detection, multi-factor source reliability, and evidence coverage validation.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-400">NLI Policy:</span>
              <span className="font-mono text-emerald-300 font-medium">Strict Entailment</span>
            </div>

            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <Award className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-400">Source Scoring:</span>
              <span className="font-mono text-indigo-300 font-medium">Multi-Factor Transparent</span>
            </div>
          </div>
        </div>

        {/* Query Ask Bar */}
        <div className="flex flex-col sm:flex-row gap-3 mt-6 pt-5 border-t border-slate-800/80">
          <input
            type="text"
            placeholder="Ask a question to evaluate multi-source agreement, contradictions, and coverage..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-50 shrink-0 flex items-center justify-center gap-2"
          >
            <Zap className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Analyzing Evidence..." : "Inspect Evidence"}
          </button>
        </div>
      </div>

      {/* Insufficient Evidence Warning Banner */}
      {report?.is_insufficient_evidence && (
        <div className="bg-amber-950/30 border border-amber-500/40 rounded-2xl p-5 flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-amber-300">
              ⚠ Insufficient Evidence Detected in Knowledge Vault
            </h4>
            <p className="text-xs text-amber-200/80 leading-relaxed">
              {report.insufficient_evidence_reason || "The retrieved evidence does not meet confidence or coverage thresholds. Zero-hallucination rejection active."}
            </p>
          </div>
        </div>
      )}

      {/* Main Analysis Results */}
      {report && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Health & Claims Tree (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            {/* Evidence Coverage & Composite Score Card */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Evidence Coverage & Score
                </span>
                <span className="text-lg font-mono font-bold text-emerald-400">
                  {report.evidence_coverage_percentage}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
                <div
                  className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, report.evidence_coverage_percentage)}%` }}
                />
              </div>

              {/* Breakdown Grid */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80 text-center">
                <div className="p-2 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[10px] text-slate-400 uppercase">Supported</div>
                  <div className="text-sm font-bold text-emerald-400">{report.supported_claims_count}</div>
                </div>
                <div className="p-2 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[10px] text-slate-400 uppercase">Contradicted</div>
                  <div className="text-sm font-bold text-rose-400">{report.contradicted_claims_count}</div>
                </div>
                <div className="p-2 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[10px] text-slate-400 uppercase">Unsupported</div>
                  <div className="text-sm font-bold text-slate-400">{report.unsupported_claims_count}</div>
                </div>
              </div>

              {report.score_breakdown && (
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-[11px] space-y-1.5 font-mono">
                  <div className="text-slate-400 font-sans font-semibold text-[10px] uppercase text-slate-400">
                    Transparent Formula Breakdown:
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Relevance Component (25%):</span>
                    <span>{report.score_breakdown.relevance_component.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Source Reliability (25%):</span>
                    <span>{report.score_breakdown.source_reliability_component.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Agreement Factor (15%):</span>
                    <span>{report.score_breakdown.agreement_component.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between text-emerald-400 font-bold pt-1 border-t border-slate-800">
                    <span>Composite Evidence Score:</span>
                    <span>{report.composite_evidence_score.toFixed(3)} / 1.000</span>
                  </div>
                </div>
              )}
            </div>

            {/* Atomic Claims List */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-cyan-400" />
                Atomic Claims Breakdown ({report.grouped_claims.length})
              </h4>

              <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                {report.grouped_claims.map((claim) => {
                  const isSelected = selectedClaim?.claim_id === claim.claim_id;
                  return (
                    <div
                      key={claim.claim_id}
                      onClick={() => setSelectedClaim(claim)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all space-y-2 ${
                        isSelected
                          ? "bg-emerald-950/40 border-emerald-500/50 shadow-md shadow-emerald-500/10"
                          : "bg-slate-950/50 border-slate-800 hover:bg-slate-900 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-xs font-semibold text-slate-200 line-clamp-2">
                          {claim.statement}
                        </span>
                        {claim.has_conflict ? (
                          <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px] font-bold shrink-0">
                            ⚠ Conflict
                          </span>
                        ) : claim.verification_status === "supported" ? (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold shrink-0">
                            ✓ Verified
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] shrink-0">
                            ? Unknown
                          </span>
                        )}
                      </div>

                      <div className="text-[10px] text-slate-400 flex items-center justify-between font-mono">
                        <span>{claim.supporting_citations.length} supporting</span>
                        {claim.contradicting_citations.length > 0 && (
                          <span className="text-rose-400 font-bold">{claim.contradicting_citations.length} conflicting</span>
                        )}
                        <span>Confidence: {(claim.confidence_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Deep Claim Evidence & Conflict Inspector (7 cols) */}
          <div className="lg:col-span-7 space-y-5">
            {selectedClaim ? (
              <div className="space-y-5">
                {/* Selected Claim Focus Card */}
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      Claim Evidence Matrix
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Grounded Confidence: {(selectedClaim.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="text-sm font-bold text-white bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                    "{selectedClaim.statement}"
                  </div>

                  {/* Conflicting Evidence Warning Banner if Conflict Exists */}
                  {selectedClaim.has_conflict && (
                    <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 space-y-2">
                      <div className="text-xs font-bold text-rose-300 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-rose-400" />
                        ⚠ Conflicting Evidence Detected Across Sources
                      </div>
                      <p className="text-xs text-rose-200/90 leading-relaxed font-mono">
                        {selectedClaim.conflict_explanation}
                      </p>
                    </div>
                  )}

                  {/* Supporting Evidence Citations */}
                  <div className="space-y-3">
                    <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Supporting Evidence Citations ({selectedClaim.supporting_citations.length})
                    </h5>

                    <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                      {selectedClaim.supporting_citations.map((cit, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-slate-950 border border-emerald-900/30 text-xs space-y-1.5"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-slate-200 flex items-center gap-1.5 truncate">
                              <FileText className="w-3.5 h-3.5 text-emerald-400" />
                              {cit.document_filename}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-emerald-400 font-mono">
                              Page {cit.page_number || "1"}
                            </span>
                          </div>
                          <blockquote className="border-l-2 border-emerald-500/50 pl-2.5 py-0.5 text-slate-300 italic text-[11px]">
                            "{cit.exact_quote}"
                          </blockquote>
                        </div>
                      ))}
                      {selectedClaim.supporting_citations.length === 0 && (
                        <div className="text-xs text-slate-500 italic p-3">
                          No direct supporting citations found for this claim.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Contradicting Evidence Citations */}
                  {selectedClaim.contradicting_citations.length > 0 && (
                    <div className="space-y-3 pt-3 border-t border-slate-800">
                      <h5 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Contradicting / Disagreeing Citations ({selectedClaim.contradicting_citations.length})
                      </h5>

                      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                        {selectedClaim.contradicting_citations.map((cit, i) => (
                          <div
                            key={i}
                            className="p-3 rounded-xl bg-slate-950 border border-rose-900/40 text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-rose-300 flex items-center gap-1.5 truncate">
                                <FileText className="w-3.5 h-3.5 text-rose-400" />
                                {cit.document_filename}
                              </span>
                              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-rose-400 font-mono">
                                Page {cit.page_number || "1"}
                              </span>
                            </div>
                            <blockquote className="border-l-2 border-rose-500/50 pl-2.5 py-0.5 text-slate-300 italic text-[11px]">
                              "{cit.exact_quote}"
                            </blockquote>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Source Quality Breakdown Cards */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Award className="w-4 h-4 text-indigo-400" />
                    Source Reliability & Quality Factors
                  </h4>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {Object.entries(selectedClaim.source_qualities).map(([fname, sq]) => (
                      <div
                        key={fname}
                        className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-200 truncate">{fname}</span>
                          <span className="font-mono text-xs font-bold text-indigo-400">
                            {(sq.overall_score * 100).toFixed(0)}% Score
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-400 space-y-0.5 font-mono">
                          <div className="flex justify-between">
                            <span>Type ({sq.document_type}):</span>
                            <span>{(sq.source_type_score * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Authority:</span>
                            <span>{(sq.authority_score * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Corroboration:</span>
                            <span>{(sq.corroboration_score * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-16 text-center text-slate-500 text-xs">
                Select an atomic claim from the left panel to inspect its supporting citations and contradiction analysis.
              </div>
            )}
          </div>
        </div>
      )}

      {/* INTERACTIVE PAIRWISE NLI CONTRADICTION SANDBOX */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <Scale className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">
                Interactive Pairwise NLI Contradiction Sandbox
              </h3>
              <p className="text-xs text-slate-400">
                Test deterministic contradiction, entailment, and condition discrepancy detection on custom statement pairs.
              </p>
            </div>
          </div>

          {/* Preset Buttons */}
          <div className="hidden sm:flex items-center gap-1.5">
            {nliPresets.map((preset, i) => (
              <button
                key={i}
                onClick={() => {
                  setPremise(preset.p);
                  setHypothesis(preset.h);
                }}
                className="px-2.5 py-1 rounded-lg text-[11px] bg-slate-950 border border-slate-800 hover:bg-slate-800 text-slate-300 transition-all font-mono"
              >
                {preset.title}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Statement A (Premise):</label>
            <textarea
              rows={3}
              value={premise}
              onChange={(e) => setPremise(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Statement B (Hypothesis):</label>
            <textarea
              rows={3}
              value={hypothesis}
              onChange={(e) => setHypothesis(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <button
            onClick={handleRunNLI}
            disabled={nliLoading}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/20 transition-all disabled:opacity-50 flex items-center gap-2"
          >
            <Scale className={`w-4 h-4 ${nliLoading ? "animate-spin" : ""}`} />
            {nliLoading ? "Evaluating NLI..." : "Evaluate Contradiction / Agreement"}
          </button>

          {nliResult && (
            <div className="flex items-center gap-3">
              {getNliVerdictBadge(nliResult.verdict)}
              <span className="text-xs font-mono text-slate-400">
                Confidence: {(nliResult.confidence * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>

        {/* NLI Detailed Result Card */}
        {nliResult && (
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2 font-mono">
            <div className="text-slate-300 font-sans leading-relaxed">
              <strong className="text-slate-200">Explanation:</strong> {nliResult.explanation}
            </div>
            {(nliResult.condition_a || nliResult.condition_b) && (
              <div className="text-[11px] text-slate-400 flex gap-4 pt-1 border-t border-slate-800">
                <span>Condition A: `{nliResult.condition_a}`</span>
                <span>Condition B: `{nliResult.condition_b}`</span>
              </div>
            )}
            {nliResult.metric_diff && (
              <div className="text-[11px] text-rose-400 font-bold">
                Metric Difference: {nliResult.metric_diff}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
