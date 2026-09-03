"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import {
  Share2,
  Search,
  RefreshCw,
  Database,
  Layers,
  Sparkles,
  ExternalLink,
  BookOpen,
  Filter,
  ArrowRight,
  Compass,
  CheckCircle2,
  Cpu,
  Zap,
  Info,
  ChevronRight,
  Maximize2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  FileText
} from "lucide-react";
import {
  EntityNode,
  RelationshipEdge,
  KnowledgeGraphSubgraph,
  GraphStats,
  HybridGraphRAGResult,
  EntityType,
  DocumentInfo
} from "../../types";
import { api } from "../../services/api";

interface KnowledgeGraphViewProps {
  documents?: DocumentInfo[];
}

// Color palettes tailored for entity taxonomies
const ENTITY_COLORS: Record<string, { bg: string; text: string; border: string; glow: string; dot: string }> = {
  model: { bg: "bg-sky-500/10", text: "text-sky-400", border: "border-sky-500/30", glow: "#38bdf8", dot: "bg-sky-400" },
  company: { bg: "bg-indigo-500/10", text: "text-indigo-400", border: "border-indigo-500/30", glow: "#818cf8", dot: "bg-indigo-400" },
  organization: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/30", glow: "#60a5fa", dot: "bg-blue-400" },
  person: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/30", glow: "#fbbf24", dot: "bg-amber-400" },
  paper: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30", glow: "#34d399", dot: "bg-emerald-400" },
  technology: { bg: "bg-rose-500/10", text: "text-rose-400", border: "border-rose-500/30", glow: "#fb7185", dot: "bg-rose-400" },
  dataset: { bg: "bg-yellow-500/10", text: "text-yellow-400", border: "border-yellow-500/30", glow: "#facc15", dot: "bg-yellow-400" },
  concept: { bg: "bg-purple-500/10", text: "text-purple-400", border: "border-purple-500/30", glow: "#c084fc", dot: "bg-purple-400" },
  event: { bg: "bg-teal-500/10", text: "text-teal-400", border: "border-teal-500/30", glow: "#2dd4bf", dot: "bg-teal-400" },
  product: { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/30", glow: "#fb923c", dot: "bg-orange-400" },
  location: { bg: "bg-cyan-500/10", text: "text-cyan-400", border: "border-cyan-500/30", glow: "#22d3ee", dot: "bg-cyan-400" },
  date: { bg: "bg-slate-500/10", text: "text-slate-400", border: "border-slate-500/30", glow: "#94a3b8", dot: "bg-slate-400" },
};

const DEFAULT_ENTITY_COLOR = {
  bg: "bg-indigo-500/10",
  text: "text-indigo-400",
  border: "border-indigo-500/30",
  glow: "#818cf8",
  dot: "bg-indigo-400",
};

interface SimNode {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  entity: EntityNode;
  radius: number;
}

interface SimEdge {
  id: string;
  source: SimNode;
  target: SimNode;
  edge: RelationshipEdge;
}

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({ documents = [] }) => {
  const [viewMode, setViewMode] = useState<"explorer" | "hybrid_rag" | "extraction_bench">("explorer");
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [entities, setEntities] = useState<EntityNode[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<EntityNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<RelationshipEdge | null>(null);
  const [neighborhood, setNeighborhood] = useState<KnowledgeGraphSubgraph | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [depth, setDepth] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);

  // Hybrid Graph RAG state
  const [ragQuery, setRagQuery] = useState("What models compete with GPT-4 and who authored Transformer?");
  const [ragResult, setRagResult] = useState<HybridGraphRAGResult | null>(null);
  const [ragLoading, setRagLoading] = useState(false);

  // Extraction Workbench state
  const [benchText, setBenchText] = useState(
    'Attention Is All You Need was authored by Ashish Vaswani and Noam Shazeer at Google DeepMind in 2017. The paper introduced the Transformer architecture, which powers models like GPT-4 created by OpenAI and BERT. GPT-4 is evaluated on the GLUE benchmark and competes with Claude released by Anthropic.'
  );
  const [benchResult, setBenchResult] = useState<any | null>(null);
  const [benchLoading, setBenchLoading] = useState(false);

  // Graph Canvas State
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDraggingCanvas, setIsDraggingCanvas] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Load Graph Stats and Initial Entities
  const loadGraphData = async () => {
    try {
      setLoading(true);
      const [statsRes, entsRes] = await Promise.all([
        api.getGraphStats().catch(() => null),
        api.searchEntities("", "all", 100).catch(() => []),
      ]);
      if (statsRes) setStats(statsRes);
      setEntities(entsRes);
      if (entsRes.length > 0 && !selectedEntity) {
        handleSelectEntity(entsRes[0]);
      }
    } catch (err) {
      console.error("Failed to load graph data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraphData();
  }, []);

  // Handle entity selection and load neighborhood
  const handleSelectEntity = async (entity: EntityNode) => {
    setSelectedEntity(entity);
    setSelectedEdge(null);
    try {
      const sub = await api.getEntityNeighborhood(entity.id, depth);
      setNeighborhood(sub);
    } catch (err) {
      console.error("Failed to load neighborhood:", err);
    }
  };

  // Re-fetch neighborhood when depth changes
  useEffect(() => {
    if (selectedEntity) {
      api.getEntityNeighborhood(selectedEntity.id, depth)
        .then((sub) => setNeighborhood(sub))
        .catch((err) => console.error(err));
    }
  }, [depth]);

  // Handle Search & Filtering
  const filteredEntities = useMemo(() => {
    return entities.filter((e) => {
      const matchesType = typeFilter === "all" || e.entity_type === typeFilter;
      const matchesQuery =
        !searchQuery ||
        e.canonical_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.aliases.some((a) => a.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesType && matchesQuery;
    });
  }, [entities, typeFilter, searchQuery]);

  // Trigger Graph Rebuild
  const handleRebuildGraph = async () => {
    try {
      setRebuilding(true);
      await api.rebuildKnowledgeGraph();
      await loadGraphData();
    } catch (err) {
      console.error("Rebuild failed:", err);
    } finally {
      setRebuilding(false);
    }
  };

  // Execute Hybrid Graph RAG
  const handleExecuteRag = async () => {
    if (!ragQuery.trim()) return;
    try {
      setRagLoading(true);
      const res = await api.executeHybridGraphRAG({
        query: ragQuery,
        top_k: 12,
        max_graph_hops: 2,
        graph_boost_factor: 0.3,
      });
      setRagResult(res);
      if (res.subgraph && res.subgraph.nodes.length > 0) {
        setNeighborhood(res.subgraph);
        setSelectedEntity(res.subgraph.nodes[0]);
      }
    } catch (err) {
      console.error("Hybrid Graph RAG error:", err);
    } finally {
      setRagLoading(false);
    }
  };

  // Execute Ad-hoc Extraction
  const handleExtractBench = async () => {
    if (!benchText.trim()) return;
    try {
      setBenchLoading(true);
      const res = await api.extractGraphFromText(benchText);
      setBenchResult(res);
    } catch (err) {
      console.error("Ad-hoc extraction failed:", err);
    } finally {
      setBenchLoading(false);
    }
  };

  // Prepare nodes and layout for interactive Canvas
  const displayNodes = useMemo(() => {
    if (neighborhood && neighborhood.nodes.length > 0) {
      return neighborhood.nodes;
    }
    return entities.slice(0, 25);
  }, [neighborhood, entities]);

  const displayEdges = useMemo(() => {
    if (neighborhood && neighborhood.edges.length > 0) {
      return neighborhood.edges;
    }
    return [];
  }, [neighborhood]);

  // Compute 2D node coordinates in circular/hierarchical constellation
  const simNodes: SimNode[] = useMemo(() => {
    const total = displayNodes.length;
    if (total === 0) return [];
    const centerX = 400;
    const centerY = 280;

    return displayNodes.map((node, i) => {
      const isCenter = selectedEntity && node.id === selectedEntity.id;
      let x = centerX;
      let y = centerY;

      if (!isCenter && total > 1) {
        const radius = Math.min(240, 100 + total * 12);
        const angle = (i / (total - (isCenter ? 1 : 0))) * 2 * Math.PI;
        x = centerX + radius * Math.cos(angle);
        y = centerY + radius * Math.sin(angle);
      }

      return {
        id: node.id,
        x,
        y,
        vx: 0,
        vy: 0,
        entity: node,
        radius: isCenter ? 28 : 20,
      };
    });
  }, [displayNodes, selectedEntity]);

  const nodeMap = useMemo(() => {
    const map = new Map<string, SimNode>();
    simNodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [simNodes]);

  const simEdges: SimEdge[] = useMemo(() => {
    return displayEdges
      .map((edge) => {
        const src = nodeMap.get(edge.source_id);
        const tgt = nodeMap.get(edge.target_id);
        if (src && tgt) {
          return { id: edge.id, source: src, target: tgt, edge };
        }
        return null;
      })
      .filter((e): e is SimEdge => e !== null);
  }, [displayEdges, nodeMap]);

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden shadow-xl shadow-cyan-950/20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-cyan-600/10 via-indigo-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
                <Share2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  Knowledge Graph Intelligence
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    Phase 5 Active
                  </span>
                </h2>
                <p className="text-xs text-slate-400">
                  Moving beyond chunk-level retrieval with explicit entity resolution, typed directional relationships & strict document provenance.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Metrics & Rebuild Button */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <Database className="w-4 h-4 text-cyan-400" />
              <span className="text-slate-400">Engine:</span>
              <span className="font-mono text-cyan-300 font-medium">
                {stats?.storage_engine || "Neo4j 5.x / Local"}
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse ml-1" />
            </div>

            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-400">Entities:</span>
              <span className="font-mono text-indigo-300 font-bold">{stats?.total_entities || 0}</span>
            </div>

            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
              <Share2 className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-400">Relations:</span>
              <span className="font-mono text-emerald-300 font-bold">{stats?.total_relationships || 0}</span>
            </div>

            <button
              onClick={handleRebuildGraph}
              disabled={rebuilding}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${rebuilding ? "animate-spin" : ""}`} />
              {rebuilding ? "Rebuilding Graph..." : "Sync / Rebuild Graph"}
            </button>
          </div>
        </div>

        {/* View Mode Tabs */}
        <div className="flex items-center gap-2 mt-6 pt-5 border-t border-slate-800/80">
          <button
            onClick={() => setViewMode("explorer")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              viewMode === "explorer"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-md shadow-cyan-500/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
            }`}
          >
            <Compass className="w-4 h-4" />
            Interactive Graph Explorer & Provenance
          </button>

          <button
            onClick={() => setViewMode("hybrid_rag")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              viewMode === "hybrid_rag"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-md shadow-cyan-500/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
            }`}
          >
            <Sparkles className="w-4 h-4 text-cyan-400" />
            Hybrid Graph RAG Assistant
          </button>

          <button
            onClick={() => setViewMode("extraction_bench")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              viewMode === "extraction_bench"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-md shadow-cyan-500/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
            }`}
          >
            <Cpu className="w-4 h-4" />
            Live Extraction & Resolution Sandbox
          </button>
        </div>
      </div>

      {/* VIEW 1: INTERACTIVE GRAPH EXPLORER */}
      {viewMode === "explorer" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Entity Taxonomy & Search (3 cols) */}
          <div className="lg:col-span-3 bg-slate-900/70 border border-slate-800 rounded-2xl p-4 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Filter className="w-3.5 h-3.5 text-cyan-400" />
                Entities & Taxonomies
              </h3>
              <span className="text-[11px] font-mono text-slate-400">
                {filteredEntities.length} of {entities.length}
              </span>
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search canonical entity or alias..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-all"
              />
            </div>

            {/* Taxonomy Filter Pills */}
            <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto pr-1">
              {[
                "all",
                "model",
                "company",
                "person",
                "paper",
                "technology",
                "dataset",
                "concept",
                "date",
              ].map((type) => (
                <button
                  key={type}
                  onClick={() => setTypeFilter(type)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] capitalize transition-all ${
                    typeFilter === type
                      ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/30"
                      : "bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800/80"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* Entity List */}
            <div className="space-y-1.5 max-h-[480px] overflow-y-auto pr-1">
              {filteredEntities.map((ent) => {
                const isSelected = selectedEntity?.id === ent.id;
                const col = ENTITY_COLORS[ent.entity_type] || DEFAULT_ENTITY_COLOR;
                return (
                  <div
                    key={ent.id}
                    onClick={() => handleSelectEntity(ent)}
                    className={`p-2.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                      isSelected
                        ? "bg-cyan-950/40 border-cyan-500/50 shadow-md shadow-cyan-500/10"
                        : "bg-slate-950/40 border-slate-800/60 hover:bg-slate-900/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center gap-2.5 overflow-hidden">
                      <span className={`w-2 h-2 rounded-full ${col.dot} shrink-0`} />
                      <div className="overflow-hidden">
                        <div className="text-xs font-semibold text-slate-200 truncate">
                          {ent.canonical_name}
                        </div>
                        <div className="text-[10px] text-slate-400 capitalize">
                          {ent.entity_type} {ent.aliases.length > 0 && `• ${ent.aliases.length} aliases`}
                        </div>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800 shrink-0">
                      {ent.mention_count} mentions
                    </span>
                  </div>
                );
              })}
              {filteredEntities.length === 0 && (
                <div className="text-center py-8 text-xs text-slate-500">
                  No entities found matching filters.
                </div>
              )}
            </div>
          </div>

          {/* Center Column: Interactive Graph Canvas (6 cols) */}
          <div className="lg:col-span-6 bg-slate-900/70 border border-slate-800 rounded-2xl p-4 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Share2 className="w-3.5 h-3.5 text-cyan-400" />
                  Local Neighborhood Subgraph
                </span>
                {selectedEntity && (
                  <span className="text-xs font-semibold text-cyan-400">
                    [{selectedEntity.canonical_name}]
                  </span>
                )}
              </div>

              {/* Traversal Depth & Controls */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400">Radius:</span>
                {[1, 2, 3].map((d) => (
                  <button
                    key={d}
                    onClick={() => setDepth(d)}
                    className={`w-6 h-6 rounded-lg text-xs font-bold transition-all ${
                      depth === d
                        ? "bg-cyan-500 text-slate-950"
                        : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
                    }`}
                  >
                    {d}
                  </button>
                ))}

                <div className="flex items-center bg-slate-950 rounded-lg border border-slate-800 ml-2">
                  <button
                    onClick={() => setZoom((z) => Math.min(2, z + 0.15))}
                    className="p-1.5 text-slate-400 hover:text-white"
                  >
                    <ZoomIn className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setZoom((z) => Math.max(0.5, z - 0.15))}
                    className="p-1.5 text-slate-400 hover:text-white"
                  >
                    <ZoomOut className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => {
                      setZoom(1);
                      setPan({ x: 0, y: 0 });
                    }}
                    className="p-1.5 text-slate-400 hover:text-white"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* SVG Visualizer Canvas */}
            <div
              className="relative w-full h-[540px] bg-slate-950/90 rounded-xl border border-slate-800/80 overflow-hidden cursor-grab active:cursor-grabbing"
              onMouseDown={(e) => {
                setIsDraggingCanvas(true);
                setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
              }}
              onMouseMove={(e) => {
                if (isDraggingCanvas) {
                  setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
                }
              }}
              onMouseUp={() => setIsDraggingCanvas(false)}
              onMouseLeave={() => setIsDraggingCanvas(false)}
            >
              {/* Subtle Grid Background */}
              <div
                className="absolute inset-0 opacity-10 pointer-events-none"
                style={{
                  backgroundImage: "radial-gradient(circle, #38bdf8 1px, transparent 1px)",
                  backgroundSize: "24px 24px",
                }}
              />

              <svg
                ref={svgRef}
                className="w-full h-full"
                viewBox="0 0 800 560"
              >
                <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                  {/* Marker for directional relationship arrows */}
                  <defs>
                    <marker
                      id="arrow"
                      viewBox="0 0 10 10"
                      refX="22"
                      refY="5"
                      markerWidth="6"
                      markerHeight="6"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8" opacity="0.8" />
                    </marker>
                    <marker
                      id="arrow-hover"
                      viewBox="0 0 10 10"
                      refX="22"
                      refY="5"
                      markerWidth="7"
                      markerHeight="7"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
                    </marker>
                  </defs>

                  {/* Relationship Edges */}
                  {simEdges.map(({ id, source, target, edge }) => {
                    const isHovered = hoveredNodeId === source.id || hoveredNodeId === target.id;
                    const isSelected = selectedEdge?.id === edge.id;
                    const midX = (source.x + target.x) / 2;
                    const midY = (source.y + target.y) / 2;

                    return (
                      <g
                        key={id}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEdge(edge);
                        }}
                        className="cursor-pointer"
                      >
                        {/* Line */}
                        <line
                          x1={source.x}
                          y1={source.y}
                          x2={target.x}
                          y2={target.y}
                          stroke={isSelected ? "#38bdf8" : isHovered ? "#818cf8" : "#334155"}
                          strokeWidth={isSelected ? 2.5 : isHovered ? 2 : 1.2}
                          strokeDasharray={isSelected ? "none" : undefined}
                          markerEnd={isSelected || isHovered ? "url(#arrow-hover)" : "url(#arrow)"}
                        />

                        {/* Edge Label Badge */}
                        <rect
                          x={midX - 38}
                          y={midY - 8}
                          width="76"
                          height="16"
                          rx="4"
                          fill="#090d16"
                          stroke={isSelected ? "#38bdf8" : "#1e293b"}
                          strokeWidth="1"
                        />
                        <text
                          x={midX}
                          y={midY + 3.5}
                          textAnchor="middle"
                          fontSize="7.5"
                          fontFamily="monospace"
                          fontWeight="bold"
                          fill={isSelected ? "#38bdf8" : "#94a3b8"}
                        >
                          {edge.relationship_type}
                        </text>
                      </g>
                    );
                  })}

                  {/* Entity Nodes */}
                  {simNodes.map(({ id, x, y, radius, entity }) => {
                    const isSelected = selectedEntity?.id === id;
                    const isHovered = hoveredNodeId === id;
                    const col = ENTITY_COLORS[entity.entity_type] || DEFAULT_ENTITY_COLOR;

                    return (
                      <g
                        key={id}
                        transform={`translate(${x}, ${y})`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectEntity(entity);
                        }}
                        onMouseEnter={() => setHoveredNodeId(id)}
                        onMouseLeave={() => setHoveredNodeId(null)}
                        className="cursor-pointer transition-transform"
                      >
                        {/* Outer Glow on Selected / Hovered */}
                        {(isSelected || isHovered) && (
                          <circle
                            r={radius + 8}
                            fill={col.glow}
                            opacity="0.2"
                            className="animate-pulse"
                          />
                        )}

                        {/* Main Node Circle */}
                        <circle
                          r={radius}
                          fill="#0f172a"
                          stroke={isSelected ? "#38bdf8" : isHovered ? col.glow : "#334155"}
                          strokeWidth={isSelected ? 3 : 1.5}
                        />

                        {/* Entity Type Inner Core */}
                        <circle
                          r={radius - 8}
                          fill={col.glow}
                          opacity={isSelected ? "0.3" : "0.15"}
                        />

                        {/* Label */}
                        <text
                          y={radius + 14}
                          textAnchor="middle"
                          fontSize="9.5"
                          fontWeight={isSelected ? "bold" : "medium"}
                          fill={isSelected ? "#f8fafc" : "#cbd5e1"}
                          className="pointer-events-none select-none"
                        >
                          {entity.canonical_name.length > 16
                            ? entity.canonical_name.slice(0, 14) + "..."
                            : entity.canonical_name}
                        </text>
                      </g>
                    );
                  })}
                </g>
              </svg>

              {/* Instructions Overlay */}
              <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1 text-[10px] text-slate-400 pointer-events-none">
                Click node or relation to inspect strict provenance • Drag to pan
              </div>
            </div>
          </div>

          {/* Right Column: Provenance & Relationship Inspector (3 cols) */}
          <div className="lg:col-span-3 bg-slate-900/70 border border-slate-800 rounded-2xl p-4 flex flex-col gap-4">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
              Provenance & Evidence Inspector
            </h3>

            {/* Selected Relationship Inspector */}
            {selectedEdge ? (
              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30">
                  <div className="text-[10px] font-mono text-cyan-400 uppercase font-semibold">
                    Relationship Triple
                  </div>
                  <div className="text-xs font-bold text-slate-100 mt-1 flex items-center gap-1.5 flex-wrap">
                    <span>{selectedEdge.source_name}</span>
                    <ArrowRight className="w-3 h-3 text-cyan-400" />
                    <span className="font-mono text-cyan-300 text-[11px]">{selectedEdge.relationship_type}</span>
                    <ArrowRight className="w-3 h-3 text-cyan-400" />
                    <span>{selectedEdge.target_name}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-2">
                    {selectedEdge.description}
                  </div>
                </div>

                <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  Verified Document Provenance ({selectedEdge.provenance_list.length})
                </div>

                <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                  {selectedEdge.provenance_list.map((p, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-semibold text-slate-200 truncate flex items-center gap-1">
                          <FileText className="w-3 h-3 text-cyan-400" />
                          {p.document_filename}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-900 text-slate-400 font-mono">
                          {p.page_number ? `Page ${p.page_number}` : "Full Document"}
                        </span>
                      </div>
                      <blockquote className="border-l-2 border-cyan-500/50 pl-2.5 py-0.5 text-slate-300 italic text-[11px]">
                        "{p.exact_snippet}"
                      </blockquote>
                      <div className="text-[10px] text-slate-500 font-mono">
                        Confidence: {(p.confidence * 100).toFixed(0)}% • Chunk: {p.chunk_id.slice(0, 8)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : selectedEntity ? (
              /* Selected Entity Details */
              <div className="space-y-4">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">
                      {selectedEntity.canonical_name}
                    </span>
                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${
                        (ENTITY_COLORS[selectedEntity.entity_type] || DEFAULT_ENTITY_COLOR).border
                      } ${(ENTITY_COLORS[selectedEntity.entity_type] || DEFAULT_ENTITY_COLOR).text}`}
                    >
                      {selectedEntity.entity_type}
                    </span>
                  </div>

                  {/* Aliases & Resolution */}
                  {selectedEntity.aliases.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80">
                      <div className="text-[10px] text-slate-400 font-medium mb-1">
                        Resolved Aliases ({selectedEntity.aliases.length}):
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {selectedEntity.aliases.map((alias, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-300 font-mono"
                          >
                            {alias}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 font-mono">
                    <span>Mentions: {selectedEntity.mention_count}</span>
                    <span>Citations: {selectedEntity.provenance_list.length}</span>
                  </div>
                </div>

                {/* Provenance Citations List */}
                <div className="space-y-2">
                  <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    Source Mentions & Passages
                  </div>

                  <div className="space-y-2 max-h-[340px] overflow-y-auto pr-1">
                    {selectedEntity.provenance_list.map((p, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-semibold text-slate-200 truncate flex items-center gap-1">
                            <FileText className="w-3 h-3 text-indigo-400" />
                            {p.document_filename}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-900 text-slate-400 font-mono">
                            {p.page_number ? `Page ${p.page_number}` : "Doc"}
                          </span>
                        </div>
                        <blockquote className="border-l-2 border-indigo-500/50 pl-2.5 py-0.5 text-slate-300 italic text-[11px]">
                          "{p.exact_snippet}"
                        </blockquote>
                      </div>
                    ))}
                    {selectedEntity.provenance_list.length === 0 && (
                      <div className="text-slate-500 text-xs text-center py-4">
                        No direct chunk provenance attached.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 text-xs">
                Select an entity node or relationship edge from the canvas to inspect citations.
              </div>
            )}
          </div>
        </div>
      )}

      {/* VIEW 2: HYBRID GRAPH RAG ASSISTANT */}
      {viewMode === "hybrid_rag" && (
        <div className="space-y-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                Hybrid Graph & Vector Evidence Reasoning
              </h3>
              <span className="text-xs text-slate-400 font-mono">
                Combines Dense Semantic Vectors + Knowledge Graph Subgraph Traversal
              </span>
            </div>

            {/* Query Input Box */}
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                placeholder="Ask relationship-heavy questions (e.g. Which models compete with GPT-4 and who authored Transformer?)"
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
                onKeyDown={(e) => e.key === "Enter" && handleExecuteRag()}
              />
              <button
                onClick={handleExecuteRag}
                disabled={ragLoading}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-cyan-600/25 transition-all disabled:opacity-50 shrink-0 flex items-center justify-center gap-2"
              >
                <Zap className={`w-4 h-4 ${ragLoading ? "animate-spin" : ""}`} />
                {ragLoading ? "Traversing Graph..." : "Execute Hybrid RAG"}
              </button>
            </div>
          </div>

          {/* RAG Synthesis & Dual Evidence Breakdown */}
          {ragResult && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Fused Synthesis & Claims (7 cols) */}
              <div className="lg:col-span-7 space-y-4">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      Neural Evidence Synthesis
                    </span>
                    <span className="text-xs font-mono text-slate-400">
                      Latency: {ragResult.execution_time_ms}ms • Confidence: {(ragResult.overall_confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="prose prose-invert max-w-none text-xs leading-relaxed text-slate-200 whitespace-pre-wrap">
                    {ragResult.synthesis_markdown}
                  </div>
                </div>

                {/* Structured Verified Claims */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Verified Claim Statements ({ragResult.claims.length})
                  </h4>
                  <div className="space-y-2">
                    {ragResult.claims.map((claim, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-slate-200">{claim.statement}</span>
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                            {(claim.confidence_score * 100).toFixed(0)}% Grounded
                          </span>
                        </div>
                        {claim.supporting_citations.length > 0 && (
                          <div className="text-[11px] text-slate-400 italic">
                            Source: `{claim.supporting_citations[0].document_filename}` — "{claim.supporting_citations[0].exact_quote}"
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Traversed Entities & Graph Triples (5 cols) */}
              <div className="lg:col-span-5 space-y-4">
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
                    <Share2 className="w-3.5 h-3.5" />
                    Traversed Graph Triples ({ragResult.graph_relationships.length})
                  </h4>
                  <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                    {ragResult.graph_relationships.map((edge, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs flex items-center justify-between"
                      >
                        <div className="flex items-center gap-1.5 font-medium text-slate-200 truncate">
                          <span>{edge.source_name}</span>
                          <span className="font-mono text-cyan-400 text-[10px] px-1.5 py-0.2 rounded bg-slate-900">
                            {edge.relationship_type}
                          </span>
                          <span>{edge.target_name}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono shrink-0">
                          {(edge.weight * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                    {ragResult.graph_relationships.length === 0 && (
                      <div className="text-slate-500 text-xs text-center py-4">
                        No direct graph relationships traversed.
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5" />
                    Semantic Passage Candidates ({ragResult.retrieved_chunks.length})
                  </h4>
                  <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                    {ragResult.retrieved_chunks.map((sc, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-semibold text-slate-300 truncate">
                            {sc.chunk.metadata?.filename || "Document"}
                          </span>
                          <span className="font-mono text-cyan-400">
                            Score: {sc.final_score.toFixed(3)}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 line-clamp-2">
                          "{sc.chunk.content}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: EXTRACTION & RESOLUTION WORKBENCH */}
      {viewMode === "extraction_bench" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6 bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Live Entity & Relationship Extraction Sandbox
            </h3>
            <p className="text-xs text-slate-400">
              Input custom raw text to test entity extraction, canonical resolution ("OpenAI", "OpenAI Inc.", "OpenAI, Inc."), and relational edge mapping with exact character spans.
            </p>

            <textarea
              rows={8}
              value={benchText}
              onChange={(e) => setBenchText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500"
            />

            <button
              onClick={handleExtractBench}
              disabled={benchLoading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-cyan-600/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Zap className={`w-4 h-4 ${benchLoading ? "animate-spin" : ""}`} />
              {benchLoading ? "Extracting & Resolving..." : "Extract Entities & Relationships"}
            </button>
          </div>

          <div className="lg:col-span-6 space-y-4">
            {benchResult ? (
              <div className="space-y-4">
                {/* Resolved Entities Card */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                      Extracted & Deduplicated Entities ({benchResult.entities.length})
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-60 overflow-y-auto pr-1">
                    {benchResult.entities.map((ent: any, i: number) => {
                      const col = ENTITY_COLORS[ent.entity_type] || DEFAULT_ENTITY_COLOR;
                      return (
                        <div
                          key={i}
                          className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-200">{ent.canonical_name}</span>
                            <span className={`text-[9px] uppercase font-bold px-1.5 py-0.2 rounded border ${col.border} ${col.text}`}>
                              {ent.entity_type}
                            </span>
                          </div>
                          {ent.aliases.length > 0 && (
                            <div className="text-[10px] text-slate-400 truncate">
                              Aliases: {ent.aliases.join(", ")}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Extracted Relationships Card */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                    Verified Directional Relationships ({benchResult.relationships.length})
                  </span>
                  <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                    {benchResult.relationships.map((rel: any, i: number) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1"
                      >
                        <div className="flex items-center gap-1.5 font-bold text-slate-200">
                          <span>{rel.source_name}</span>
                          <span className="font-mono text-cyan-400 text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                            {rel.relationship_type}
                          </span>
                          <span>{rel.target_name}</span>
                        </div>
                        {rel.provenance_list?.length > 0 && (
                          <blockquote className="border-l-2 border-emerald-500/50 pl-2 text-slate-400 italic text-[11px]">
                            "{rel.provenance_list[0].exact_snippet}"
                          </blockquote>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center gap-3">
                <Share2 className="w-8 h-8 text-slate-700" />
                Click "Extract Entities & Relationships" to run live extraction on the text snippet.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
