"""
API Endpoints for Phase 5 — Knowledge Graph Intelligence.
Provides entity discovery, neighborhood visualization, paths, ad-hoc extraction, and Hybrid Graph RAG query execution.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from app.domain.models import (
    EntityNode,
    EntityType,
    RelationshipType,
    KnowledgeGraphSubgraph,
    GraphPath,
    GraphStats,
    HybridGraphRAGResult,
    RetrievalMode
)
from app.services.graph_service import GraphService
from app.services.hybrid_graph_rag_service import HybridGraphRAGService
from app.services.ingestion_service import IngestionService
from app.core.logging import logger

router = APIRouter(prefix="/graph", tags=["Knowledge Graph Intelligence"])

graph_service = GraphService()
hybrid_rag_service = HybridGraphRAGService(graph_service=graph_service)
ingestion_service = IngestionService(graph_service=graph_service)


class HybridGraphQueryRequest(BaseModel):
    query: str
    top_k: int = 15
    max_graph_hops: int = 2
    graph_boost_factor: float = 0.25
    use_dense: bool = True
    use_sparse: bool = True
    use_reranker: bool = True


class ExtractRequest(BaseModel):
    text: str


class PathSearchRequest(BaseModel):
    source_name: str
    target_name: str
    max_depth: int = 3


@router.get("/stats", response_model=GraphStats)
def get_graph_stats():
    """Returns global Knowledge Graph statistics and connection health."""
    return graph_service.get_stats()


@router.get("/schema")
def get_graph_schema():
    """Returns the configurable supported entity types and relationship types taxonomy."""
    return {
        "entity_types": [e.value for e in EntityType],
        "relationship_types": [r.value for r in RelationshipType],
        "taxonomy_descriptions": {
            "person": "Authors, researchers, scientists, and industry leaders",
            "organization": "Institutions, universities, and research labs",
            "company": "Commercial enterprises and corporate entities",
            "technology": "Algorithms, architectures, libraries, and frameworks",
            "model": "Machine learning and neural foundation models",
            "paper": "Academic publications and technical reports",
            "dataset": "Benchmark and training datasets",
            "concept": "Theoretical principles, techniques, and terminology",
            "event": "Conferences, milestones, and release events",
            "product": "Commercial or open-source software applications",
            "location": "Geographical headquarters and conference locations",
            "date": "Temporal publication and milestone timestamps"
        }
    }


@router.get("/entities", response_model=List[EntityNode])
def search_entities(
    query: str = Query(default="", description="Search query matching canonical name or aliases"),
    entity_type: Optional[str] = Query(default=None, description="Filter by EntityType (e.g., model, person, company)"),
    limit: int = Query(default=50, ge=1, le=200)
):
    """Searches and lists canonical entities with provenance mentions."""
    return graph_service.search_entities(query=query, entity_type=entity_type, limit=limit)


@router.get("/entities/{entity_id}", response_model=EntityNode)
def get_entity_details(entity_id: str):
    """Retrieves full entity details including all aliases and provenance citations."""
    entity = graph_service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found.")
    return entity


@router.get("/neighborhood/{entity_id}", response_model=KnowledgeGraphSubgraph)
def get_entity_neighborhood(
    entity_id: str,
    depth: int = Query(default=1, ge=1, le=3, description="Neighborhood traversal radius")
):
    """Extracts local k-hop ego network subgraph for interactive graph visualization."""
    return graph_service.get_neighborhood(entity_id=entity_id, depth=depth)


@router.post("/query", response_model=HybridGraphRAGResult)
def execute_hybrid_graph_rag(request: HybridGraphQueryRequest):
    """
    Executes Hybrid Graph RAG combining Dense Vector + Sparse BM25 + Knowledge Graph Traversal & Fusion.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    mode = RetrievalMode(
        use_dense=request.use_dense,
        use_sparse=request.use_sparse,
        use_reranker=request.use_reranker,
        top_k=request.top_k,
        rerank_top_k=min(8, request.top_k)
    )

    return hybrid_rag_service.query(
        query=request.query,
        mode=mode,
        max_graph_hops=request.max_graph_hops,
        graph_boost_factor=request.graph_boost_factor
    )


@router.post("/extract")
def extract_entities_and_relationships(request: ExtractRequest):
    """Ad-hoc entity and relationship extraction preview from arbitrary text."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return graph_service.extract_from_text(request.text)


@router.post("/build")
def rebuild_knowledge_graph():
    """Rebuilds the Knowledge Graph by processing all stored document chunks in the repository."""
    all_chunks = ingestion_service.vector_store.list_all_chunks()
    if not all_chunks:
        return {"status": "empty", "message": "No chunks found in corpus to build graph from."}
    return graph_service.build_full_graph_from_chunks(all_chunks)


@router.post("/paths", response_model=List[GraphPath])
def find_entity_paths(request: PathSearchRequest):
    """Discovers multi-hop relational paths connecting two entities."""
    return graph_service.find_paths(
        source_name=request.source_name,
        target_name=request.target_name,
        max_depth=request.max_depth
    )
