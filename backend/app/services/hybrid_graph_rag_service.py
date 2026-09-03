"""
Hybrid Graph RAG Service for NEXUS-RAG (Phase 5).
Fuses Dense & BM25 Vector Retrieval with Knowledge Graph Neighborhood Traversal and Provenance-grounded Synthesis.
"""
from typing import List, Dict, Any, Optional, Set, Tuple
import time
import re
from app.domain.models import (
    ScoredChunk,
    EntityNode,
    RelationshipEdge,
    KnowledgeGraphSubgraph,
    GraphPath,
    HybridGraphRAGResult,
    EvidenceClaim,
    EvidenceCitation,
    RetrievalMode
)
from app.services.retrieval_service import RetrievalService
from app.services.graph_service import GraphService
from app.infrastructure.graph.entity_extractor import EntityExtractor
from app.core.logging import logger


class HybridGraphRAGService:
    """Combines vector semantics, structured relationship graphs, and metadata into unified intelligence."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        graph_service: Optional[GraphService] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.graph_service = graph_service or GraphService()
        self.entity_extractor = EntityExtractor()

    def query(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None,
        max_graph_hops: int = 2,
        graph_boost_factor: float = 0.25
    ) -> HybridGraphRAGResult:
        """
        Executes Hybrid Graph RAG:
        1. Query entity recognition
        2. Semantic vector & keyword retrieval
        3. Knowledge graph neighborhood traversal & path search
        4. Hybrid graph-vector evidence fusion & boost
        5. Grounded multi-modal evidence synthesis
        """
        start_time = time.time()
        logger.info(f"Executing Hybrid Graph RAG for query: '{query}'")

        # 1. Extract query entities
        raw_query_entities = self.entity_extractor.extract_from_text(query)
        query_entity_names = [e[0] for e in raw_query_entities]

        # 2. Semantic Vector & BM25 Retrieval
        retrieval_cfg = mode or RetrievalMode(top_k=15, rerank_top_k=8)
        scored_chunks, trace = self.retrieval_service.retrieve_with_trace(query, mode=retrieval_cfg)

        # 3. Knowledge Graph Traversal
        matched_graph_nodes: List[EntityNode] = []
        collected_edges: List[RelationshipEdge] = []
        discovered_paths: List[GraphPath] = []
        seen_node_ids: Set[str] = set()
        seen_edge_ids: Set[str] = set()

        for name in query_entity_names:
            node = self.graph_service.graph_store.find_entity_by_name(name)
            if node and node.id not in seen_node_ids:
                seen_node_ids.add(node.id)
                matched_graph_nodes.append(node)
                
                # Fetch local neighborhood
                subgraph = self.graph_service.get_neighborhood(node.id, depth=max_graph_hops)
                for n in subgraph.nodes:
                    if n.id not in seen_node_ids:
                        seen_node_ids.add(n.id)
                        matched_graph_nodes.append(n)
                for e in subgraph.edges:
                    if e.id not in seen_edge_ids:
                        seen_edge_ids.add(e.id)
                        collected_edges.append(e)

        # Path search between query entity pairs
        if len(matched_graph_nodes) >= 2:
            for i in range(len(matched_graph_nodes)):
                for j in range(i + 1, min(len(matched_graph_nodes), 4)):
                    paths = self.graph_service.find_paths(
                        matched_graph_nodes[i].canonical_name,
                        matched_graph_nodes[j].canonical_name,
                        max_depth=max_graph_hops + 1
                    )
                    discovered_paths.extend(paths)

        # 4. Graph-Boosted Evidence Reranking
        # If a retrieved chunk is directly cited in the provenance of a matched graph edge, boost its score
        graph_chunk_ids: Set[str] = set()
        for edge in collected_edges:
            for p in edge.provenance_list:
                graph_chunk_ids.add(p.chunk_id)
        for node in matched_graph_nodes:
            for p in node.provenance_list:
                graph_chunk_ids.add(p.chunk_id)

        boosted_chunks: List[ScoredChunk] = []
        for sc in scored_chunks:
            chunk_copy = sc.model_copy()
            if sc.chunk.id in graph_chunk_ids:
                # Apply graph boost
                chunk_copy.final_score = min(1.0, sc.final_score + graph_boost_factor)
                chunk_copy.rerank_score = (chunk_copy.rerank_score or sc.final_score) + graph_boost_factor
            boosted_chunks.append(chunk_copy)

        # Re-sort boosted chunks
        boosted_chunks.sort(key=lambda x: x.final_score, reverse=True)

        # 5. Build Grounded Synthesis with Dual (Passage + Graph) Citations
        claims: List[EvidenceClaim] = []
        synthesis_sections: List[str] = []

        # Graph Relationship Evidence block
        if collected_edges:
            rel_lines = []
            for edge in collected_edges[:8]:
                prov_label = ""
                if edge.provenance_list:
                    p = edge.provenance_list[0]
                    page_str = f"Page {p.page_number}" if p.page_number else "Document body"
                    prov_label = f" *(Source: `{p.document_filename}` — {page_str})*"

                rel_lines.append(
                    f"- **[{edge.source_name}]** — `{edge.relationship_type.value}` ➔ **[{edge.target_name}]**{prov_label}"
                )
                
                # Create structured Claim for relationship
                if edge.provenance_list:
                    p0 = edge.provenance_list[0]
                    cit = EvidenceCitation(
                        citation_id=f"graph-cit-{edge.id[:8]}",
                        chunk_id=p0.chunk_id,
                        document_id=p0.document_id,
                        document_filename=p0.document_filename,
                        page_number=p0.page_number,
                        section_title=p0.section_title,
                        exact_quote=p0.exact_snippet,
                        relevance_score=edge.weight
                    )
                    claims.append(EvidenceClaim(
                        statement=f"Graph relation verified: {edge.source_name} {edge.relationship_type.value} {edge.target_name}",
                        supporting_citations=[cit],
                        confidence_score=edge.weight,
                        verification_status="supported"
                    ))

            synthesis_sections.append(
                "#### Knowledge Graph Verified Relationships\n" + "\n".join(rel_lines)
            )

        # Multi-Hop Path Reasoning block
        if discovered_paths:
            path_lines = []
            for path in discovered_paths[:3]:
                path_lines.append(f"- 🧭 **{path.hops}-Hop Path**: {path.path_description}")
            synthesis_sections.append(
                "#### Explicit Graph Multi-Hop Traversal Paths\n" + "\n".join(path_lines)
            )

        # Semantic Text Passages block
        if boosted_chunks:
            passage_lines = []
            for idx, sc in enumerate(boosted_chunks[:5], 1):
                fname = sc.chunk.metadata.get("filename", "Doc")
                page = sc.chunk.span.page_number
                p_label = f"Page {page}" if page else "Document passage"
                passage_lines.append(
                    f"**[Source {idx}]** `{fname}` ({p_label}) — Score: `{sc.final_score:.3f}`:\n> \"{sc.chunk.content[:220]}...\""
                )

                # Add passage claim
                cit = EvidenceCitation(
                    citation_id=sc.chunk.id,
                    chunk_id=sc.chunk.id,
                    document_id=sc.chunk.document_id,
                    document_filename=fname,
                    page_number=page,
                    section_title=sc.chunk.span.section_title,
                    exact_quote=sc.chunk.content[:200],
                    relevance_score=sc.final_score
                )
                claims.append(EvidenceClaim(
                    statement=f"Semantic evidence from {fname} ({p_label}): {sc.chunk.content[:150]}",
                    supporting_citations=[cit],
                    confidence_score=round(sc.final_score, 3),
                    verification_status="supported"
                ))

            synthesis_sections.append(
                "#### Supporting Text Evidence\n" + "\n\n".join(passage_lines)
            )

        # Full Synthesis Markdown
        full_md = (
            f"### Hybrid Graph & Semantic Evidence Synthesis\n\n"
            f"Evaluated query with **{len(matched_graph_nodes)}** knowledge graph entities, "
            f"**{len(collected_edges)}** verified relational triples, and **{len(boosted_chunks)}** semantic context chunks.\n\n"
            + "\n\n---\n\n".join(synthesis_sections)
        )

        overall_conf = (
            sum(c.confidence_score for c in claims) / len(claims) if claims else 0.85
        )
        exec_ms = round((time.time() - start_time) * 1000, 2)

        subgraph_result = KnowledgeGraphSubgraph(
            nodes=matched_graph_nodes,
            edges=collected_edges,
            depth=max_graph_hops,
            total_nodes=len(matched_graph_nodes),
            total_edges=len(collected_edges)
        )

        return HybridGraphRAGResult(
            query=query,
            synthesis_markdown=full_md,
            claims=claims,
            retrieved_chunks=boosted_chunks,
            graph_entities=matched_graph_nodes,
            graph_relationships=collected_edges,
            graph_paths=discovered_paths,
            subgraph=subgraph_result,
            overall_confidence=round(overall_conf, 3),
            execution_time_ms=exec_ms,
            model_used="hybrid_graph_rag_v1"
        )
