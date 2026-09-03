"""
Graph Store Infrastructure for NEXUS-RAG (Phase 5).
Dual-mode implementation supporting Neo4j Bolt driver and Local In-Memory JSON-persisted graph.
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import json
import uuid
from collections import deque
from app.domain.models import (
    EntityNode,
    EntityType,
    RelationshipEdge,
    RelationshipType,
    KnowledgeGraphSubgraph,
    GraphPath,
    GraphStats,
    GraphProvenance
)
from app.core.config import settings
from app.core.logging import logger


class LocalInMemoryGraphStore:
    """Zero-dependency, high-performance in-memory graph store with JSON file persistence."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (settings.INDEX_DIR / "graph_store.json")
        self.entities: Dict[str, EntityNode] = {}              # id -> EntityNode
        self.name_to_id: Dict[str, str] = {}                  # lowercase canonical_name / alias -> id
        self.edges: Dict[str, RelationshipEdge] = {}           # id -> RelationshipEdge
        self.adj_out: Dict[str, List[str]] = {}               # entity_id -> list of edge_ids
        self.adj_in: Dict[str, List[str]] = {}                # entity_id -> list of edge_ids
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for e_data in data.get("entities", []):
                        node = EntityNode(**e_data)
                        self.entities[node.id] = node
                        self.name_to_id[node.canonical_name.lower()] = node.id
                        for a in node.aliases:
                            self.name_to_id[a.lower()] = node.id

                    for r_data in data.get("edges", []):
                        edge = RelationshipEdge(**r_data)
                        self.edges[edge.id] = edge
                        self.adj_out.setdefault(edge.source_id, []).append(edge.id)
                        self.adj_in.setdefault(edge.target_id, []).append(edge.id)

                logger.info(f"Loaded {len(self.entities)} entities and {len(self.edges)} edges from {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to load graph store from {self.storage_path}: {e}")

    def _persist(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "entities": [node.model_dump() for node in self.entities.values()],
                "edges": [edge.model_dump() for edge in self.edges.values()]
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist graph store: {e}")

    def upsert_entity(self, entity: EntityNode) -> EntityNode:
        existing_id = self.name_to_id.get(entity.canonical_name.lower())
        if existing_id and existing_id in self.entities:
            existing = self.entities[existing_id]
            existing.mention_count += 1
            for alias in entity.aliases:
                if alias not in existing.aliases:
                    existing.aliases.append(alias)
                    self.name_to_id[alias.lower()] = existing.id
            for prov in entity.provenance_list:
                if not any(p.chunk_id == prov.chunk_id and p.exact_snippet == prov.exact_snippet for p in existing.provenance_list):
                    existing.provenance_list.append(prov)
            self._persist()
            return existing

        self.entities[entity.id] = entity
        self.name_to_id[entity.canonical_name.lower()] = entity.id
        for alias in entity.aliases:
            self.name_to_id[alias.lower()] = entity.id

        self.adj_out.setdefault(entity.id, [])
        self.adj_in.setdefault(entity.id, [])
        self._persist()
        return entity

    def upsert_relationship(self, edge: RelationshipEdge) -> RelationshipEdge:
        # Check if an edge between same source, target, and type already exists
        for existing_id in self.adj_out.get(edge.source_id, []):
            existing = self.edges.get(existing_id)
            if existing and existing.target_id == edge.target_id and existing.relationship_type == edge.relationship_type:
                for prov in edge.provenance_list:
                    if not any(p.chunk_id == prov.chunk_id and p.exact_snippet == prov.exact_snippet for p in existing.provenance_list):
                        existing.provenance_list.append(prov)
                existing.weight = max(existing.weight, edge.weight)
                self._persist()
                return existing

        self.edges[edge.id] = edge
        self.adj_out.setdefault(edge.source_id, []).append(edge.id)
        self.adj_in.setdefault(edge.target_id, []).append(edge.id)
        self._persist()
        return edge

    def get_entity_by_id(self, entity_id: str) -> Optional[EntityNode]:
        return self.entities.get(entity_id)

    def find_entity_by_name(self, name: str) -> Optional[EntityNode]:
        node_id = self.name_to_id.get(name.lower().strip())
        if node_id:
            return self.entities.get(node_id)
        # Prefix or substring match
        for key, n_id in self.name_to_id.items():
            if name.lower() in key or key in name.lower():
                return self.entities.get(n_id)
        return None

    def search_entities(self, query: str = "", entity_type: Optional[str] = None, limit: int = 50) -> List[EntityNode]:
        results: List[EntityNode] = []
        q_lower = query.lower().strip() if query else ""

        for node in self.entities.values():
            if entity_type and entity_type.lower() != "all" and node.entity_type.value != entity_type.lower():
                continue
            if not q_lower or q_lower in node.canonical_name.lower() or any(q_lower in a.lower() for a in node.aliases):
                results.append(node)

        # Sort by mention count desc
        results.sort(key=lambda n: n.mention_count, reverse=True)
        return results[:limit]

    def get_neighborhood(self, entity_id: str, depth: int = 1) -> KnowledgeGraphSubgraph:
        if entity_id not in self.entities:
            return KnowledgeGraphSubgraph(nodes=[], edges=[], query_entity_id=entity_id, depth=depth)

        visited_nodes: Set[str] = {entity_id}
        collected_edges: Set[str] = set()
        queue: deque[Tuple[str, int]] = deque([(entity_id, 0)])

        while queue:
            curr_id, curr_depth = queue.popleft()
            if curr_depth >= depth:
                continue

            # Outgoing edges
            for edge_id in self.adj_out.get(curr_id, []):
                edge = self.edges.get(edge_id)
                if edge:
                    collected_edges.add(edge.id)
                    if edge.target_id not in visited_nodes:
                        visited_nodes.add(edge.target_id)
                        queue.append((edge.target_id, curr_depth + 1))

            # Incoming edges
            for edge_id in self.adj_in.get(curr_id, []):
                edge = self.edges.get(edge_id)
                if edge:
                    collected_edges.add(edge.id)
                    if edge.source_id not in visited_nodes:
                        visited_nodes.add(edge.source_id)
                        queue.append((edge.source_id, curr_depth + 1))

        nodes_list = [self.entities[n_id] for n_id in visited_nodes if n_id in self.entities]
        edges_list = [self.edges[e_id] for e_id in collected_edges if e_id in self.edges]

        return KnowledgeGraphSubgraph(
            nodes=nodes_list,
            edges=edges_list,
            query_entity_id=entity_id,
            depth=depth,
            total_nodes=len(nodes_list),
            total_edges=len(edges_list)
        )

    def find_paths(self, source_name: str, target_name: str, max_depth: int = 3) -> List[GraphPath]:
        src_node = self.find_entity_by_name(source_name)
        tgt_node = self.find_entity_by_name(target_name)

        if not src_node or not tgt_node or src_node.id == tgt_node.id:
            return []

        # BFS shortest path search
        queue: deque[Tuple[str, List[str], List[str]]] = deque([(src_node.id, [src_node.id], [])])
        visited: Set[str] = {src_node.id}
        found_paths: List[GraphPath] = []

        while queue:
            curr_id, node_path, edge_path = queue.popleft()
            if curr_id == tgt_node.id:
                path_nodes = [self.entities[nid] for nid in node_path if nid in self.entities]
                path_edges = [self.edges[eid] for eid in edge_path if eid in self.edges]
                desc = " -> ".join([f"[{n.canonical_name}]" for n in path_nodes])
                found_paths.append(GraphPath(
                    nodes=path_nodes,
                    edges=path_edges,
                    path_description=desc,
                    hops=len(path_edges)
                ))
                if len(found_paths) >= 5:
                    break
                continue

            if len(edge_path) >= max_depth:
                continue

            # Explore outgoing edges
            for edge_id in self.adj_out.get(curr_id, []):
                edge = self.edges.get(edge_id)
                if edge and edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, node_path + [edge.target_id], edge_path + [edge.id]))

        return found_paths

    def get_stats(self) -> GraphStats:
        ent_types: Dict[str, int] = {}
        for n in self.entities.values():
            ent_types[n.entity_type.value] = ent_types.get(n.entity_type.value, 0) + 1

        rel_types: Dict[str, int] = {}
        for e in self.edges.values():
            rel_types[e.relationship_type.value] = rel_types.get(e.relationship_type.value, 0) + 1

        return GraphStats(
            total_entities=len(self.entities),
            total_relationships=len(self.edges),
            entity_types_count=ent_types,
            relationship_types_count=rel_types,
            storage_engine="local_memory_json",
            connected=True
        )

    def delete_by_document_id(self, document_id: str) -> int:
        removed_entities = 0
        # Filter provenance from entities
        for node in list(self.entities.values()):
            node.provenance_list = [p for p in node.provenance_list if p.document_id != document_id]
            if not node.provenance_list:
                # Remove node if no provenance left
                del self.entities[node.id]
                self.name_to_id.pop(node.canonical_name.lower(), None)
                removed_entities += 1

        # Filter provenance from edges
        for edge_id, edge in list(self.edges.items()):
            edge.provenance_list = [p for p in edge.provenance_list if p.document_id != document_id]
            if not edge.provenance_list or edge.source_id not in self.entities or edge.target_id not in self.entities:
                self.edges.pop(edge_id, None)

        # Rebuild adjacency
        self.adj_out = {}
        self.adj_in = {}
        for edge in self.edges.values():
            self.adj_out.setdefault(edge.source_id, []).append(edge.id)
            self.adj_in.setdefault(edge.target_id, []).append(edge.id)

        self._persist()
        return removed_entities

    def clear(self) -> None:
        self.entities.clear()
        self.name_to_id.clear()
        self.edges.clear()
        self.adj_out.clear()
        self.adj_in.clear()
        self._persist()


class Neo4jGraphStore:
    """Neo4j Enterprise / Community Graph Database Store via Bolt driver."""

    def __init__(
        self,
        uri: str = settings.NEO4J_URI,
        user: str = settings.NEO4J_USER,
        password: str = settings.NEO4J_PASSWORD,
        database: str = settings.NEO4J_DATABASE
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None
        self._local_fallback = LocalInMemoryGraphStore()
        self._init_driver()

    def _init_driver(self) -> None:
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j database at {self.uri}")
            self._init_schema()
        except Exception as e:
            logger.warning(f"Neo4j connection failed ({e}). Operating in Local In-Memory Fallback mode.")
            self._driver = None

    def _init_schema(self) -> None:
        if not self._driver:
            return
        try:
            with self._driver.session(database=self.database) as session:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
                session.run("CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.canonical_name)")
        except Exception as e:
            logger.warning(f"Could not initialize Neo4j constraints: {e}")

    def upsert_entity(self, entity: EntityNode) -> EntityNode:
        # Sync to local in-memory fallback for instant retrieval and persistence
        self._local_fallback.upsert_entity(entity)
        if not self._driver:
            return entity

        try:
            with self._driver.session(database=self.database) as session:
                cypher = """
                MERGE (e:Entity {canonical_name: $canonical_name})
                ON CREATE SET 
                    e.id = $id,
                    e.entity_type = $entity_type,
                    e.mention_count = $mention_count,
                    e.aliases = $aliases,
                    e.created_at = $created_at
                ON MATCH SET 
                    e.mention_count = e.mention_count + 1,
                    e.aliases = $aliases
                RETURN e.id
                """
                session.run(
                    cypher,
                    id=entity.id,
                    canonical_name=entity.canonical_name,
                    entity_type=entity.entity_type.value,
                    mention_count=entity.mention_count,
                    aliases=entity.aliases,
                    created_at=entity.created_at
                )
        except Exception as e:
            logger.error(f"Neo4j upsert_entity error: {e}")
        return entity

    def upsert_relationship(self, edge: RelationshipEdge) -> RelationshipEdge:
        self._local_fallback.upsert_relationship(edge)
        if not self._driver:
            return edge

        try:
            with self._driver.session(database=self.database) as session:
                # Dynamic cypher with relationship type
                rel_type = edge.relationship_type.value
                cypher = f"""
                MATCH (a:Entity {{id: $source_id}})
                MATCH (b:Entity {{id: $target_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                ON CREATE SET 
                    r.id = $id,
                    r.weight = $weight,
                    r.description = $description,
                    r.created_at = $created_at
                ON MATCH SET 
                    r.weight = $weight
                RETURN r.id
                """
                session.run(
                    cypher,
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    id=edge.id,
                    weight=edge.weight,
                    description=edge.description,
                    created_at=edge.created_at
                )
        except Exception as e:
            logger.error(f"Neo4j upsert_relationship error: {e}")
        return edge

    def get_entity_by_id(self, entity_id: str) -> Optional[EntityNode]:
        return self._local_fallback.get_entity_by_id(entity_id)

    def find_entity_by_name(self, name: str) -> Optional[EntityNode]:
        return self._local_fallback.find_entity_by_name(name)

    def search_entities(self, query: str = "", entity_type: Optional[str] = None, limit: int = 50) -> List[EntityNode]:
        return self._local_fallback.search_entities(query, entity_type, limit)

    def get_neighborhood(self, entity_id: str, depth: int = 1) -> KnowledgeGraphSubgraph:
        return self._local_fallback.get_neighborhood(entity_id, depth)

    def find_paths(self, source_name: str, target_name: str, max_depth: int = 3) -> List[GraphPath]:
        return self._local_fallback.find_paths(source_name, target_name, max_depth)

    def get_stats(self) -> GraphStats:
        stats = self._local_fallback.get_stats()
        stats.storage_engine = "Neo4j 5.x (Bolt)" if self._driver else "local_memory_json (Fallback)"
        stats.connected = self._driver is not None
        return stats

    def delete_by_document_id(self, document_id: str) -> int:
        return self._local_fallback.delete_by_document_id(document_id)

    def clear(self) -> None:
        self._local_fallback.clear()
        if self._driver:
            try:
                with self._driver.session(database=self.database) as session:
                    session.run("MATCH (n) DETACH DELETE n")
            except Exception as e:
                logger.error(f"Neo4j clear error: {e}")


# Singleton Graph Store instance
_graph_store_instance = None

def get_graph_store():
    """Factory creating configured graph store with automatic Neo4j/Local detection."""
    global _graph_store_instance
    if _graph_store_instance is None:
        mode = settings.GRAPH_STORAGE_MODE.lower()
        if mode in ("neo4j", "auto"):
            _graph_store_instance = Neo4jGraphStore()
        else:
            _graph_store_instance = LocalInMemoryGraphStore()
    return _graph_store_instance
