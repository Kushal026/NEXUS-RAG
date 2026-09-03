"""
Knowledge Graph Service for NEXUS-RAG (Phase 5).
Orchestrates entity extraction, canonical resolution, relationship extraction, and graph querying.
"""
from typing import List, Dict, Any, Optional, Tuple
from app.domain.models import (
    DocumentChunk,
    EntityNode,
    RelationshipEdge,
    EntityType,
    RelationshipType,
    KnowledgeGraphSubgraph,
    GraphPath,
    GraphStats
)
from app.infrastructure.graph.entity_extractor import EntityExtractor
from app.infrastructure.graph.entity_resolver import EntityResolver
from app.infrastructure.graph.relationship_extractor import RelationshipExtractor
from app.infrastructure.graph.graph_store import get_graph_store
from app.core.logging import logger


class GraphService:
    """Manages the end-to-end Knowledge Graph construction, indexing, and retrieval lifecycle."""

    def __init__(self, graph_store=None):
        self.graph_store = graph_store or get_graph_store()
        self.entity_extractor = EntityExtractor()
        self.entity_resolver = EntityResolver()
        self.rel_extractor = RelationshipExtractor()

    def index_chunk_graph(self, chunk: DocumentChunk) -> Tuple[List[EntityNode], List[RelationshipEdge]]:
        """
        Executes full Graph Construction pipeline for a single DocumentChunk:
        Chunk -> Entity Extraction -> Entity Resolution -> Graph Upsert -> Relationship Extraction -> Graph Upsert.
        """
        # 1. Entity Extraction
        raw_extractions = self.entity_extractor.extract_from_chunk(chunk)
        if not raw_extractions:
            return [], []

        # 2. Entity Resolution & Canonical Deduplication
        resolved_nodes: List[EntityNode] = []
        for raw_name, ent_type, provenance in raw_extractions:
            node = self.entity_resolver.resolve_entity(raw_name, ent_type, provenance)
            # Upsert into Graph Store
            saved_node = self.graph_store.upsert_entity(node)
            if saved_node not in resolved_nodes:
                resolved_nodes.append(saved_node)

        # 3. Relationship Extraction with Strict Chunk Provenance
        edges = self.rel_extractor.extract_relationships_from_chunk(chunk, resolved_nodes)
        saved_edges: List[RelationshipEdge] = []
        for edge in edges:
            saved_edge = self.graph_store.upsert_relationship(edge)
            saved_edges.append(saved_edge)

        logger.debug(f"Chunk {chunk.id[:8]}: indexed {len(resolved_nodes)} entities, {len(saved_edges)} relationships.")
        return resolved_nodes, saved_edges

    def build_full_graph_from_chunks(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Rebuilds the entire Knowledge Graph from all existing chunks."""
        logger.info(f"Rebuilding Knowledge Graph from {len(chunks)} chunks...")
        self.graph_store.clear()
        self.entity_resolver.clear()

        total_entities_indexed = 0
        total_edges_indexed = 0

        for chunk in chunks:
            nodes, edges = self.index_chunk_graph(chunk)
            total_entities_indexed += len(nodes)
            total_edges_indexed += len(edges)

        stats = self.graph_store.get_stats()
        logger.info(f"Graph Rebuild Complete: {stats.total_entities} unique entities, {stats.total_relationships} relationships.")
        return {
            "status": "success",
            "chunks_processed": len(chunks),
            "unique_entities": stats.total_entities,
            "unique_relationships": stats.total_relationships,
            "storage_engine": stats.storage_engine
        }

    def search_entities(
        self,
        query: str = "",
        entity_type: Optional[str] = None,
        limit: int = 50
    ) -> List[EntityNode]:
        """Search and list entities filtered by name query and taxonomy category."""
        return self.graph_store.search_entities(query=query, entity_type=entity_type, limit=limit)

    def get_entity(self, entity_id: str) -> Optional[EntityNode]:
        """Fetches a single entity with its full provenance citation history."""
        return self.graph_store.get_entity_by_id(entity_id)

    def get_neighborhood(self, entity_id: str, depth: int = 1) -> KnowledgeGraphSubgraph:
        """Extracts k-hop local neighborhood subgraph for visualization and graph traversal."""
        return self.graph_store.get_neighborhood(entity_id=entity_id, depth=depth)

    def find_paths(self, source_name: str, target_name: str, max_depth: int = 3) -> List[GraphPath]:
        """Finds traversal paths between two entities."""
        return self.graph_store.find_paths(source_name=source_name, target_name=target_name, max_depth=max_depth)

    def get_stats(self) -> GraphStats:
        """Retrieves global Knowledge Graph health and distribution statistics."""
        return self.graph_store.get_stats()

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """Ad-hoc extraction preview on arbitrary text without mutating persistent storage."""
        raw_extractions = self.entity_extractor.extract_from_text(text)
        temp_resolver = EntityResolver()
        temp_nodes: List[EntityNode] = []
        for raw_name, ent_type, provenance in raw_extractions:
            node = temp_resolver.resolve_entity(raw_name, ent_type, provenance)
            if node not in temp_nodes:
                temp_nodes.append(node)

        chunk_placeholder = DocumentChunk(
            id="preview",
            document_id="adhoc",
            chunk_index=0,
            content=text,
            span={"start_char": 0, "end_char": len(text)}
        )
        edges = self.rel_extractor.extract_relationships_from_chunk(chunk_placeholder, temp_nodes)

        return {
            "entities": [n.model_dump() for n in temp_nodes],
            "relationships": [e.model_dump() for e in edges]
        }

    def delete_document_graph(self, document_id: str) -> int:
        """Cleans up provenance references and orphaned entities upon document removal."""
        return self.graph_store.delete_by_document_id(document_id)
