"""
API v1 Router aggregation.
"""
from fastapi import APIRouter
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.query import router as query_router
from app.api.v1.endpoints.system import router as system_router
from app.api.v1.endpoints.evaluation import router as evaluation_router
from app.api.v1.endpoints.reasoning import router as reasoning_router
from app.api.v1.endpoints.temporal import router as temporal_router
from app.api.v1.endpoints.graph import router as graph_router
from app.api.v1.endpoints.evidence_intelligence import router as evidence_intelligence_router
from app.api.v1.endpoints.self_correction import router as self_correction_router
from app.api.v1.endpoints.multimodal import router as multimodal_router
from app.api.v1.endpoints.agent import router as agent_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.production_health import router as production_health_router

api_router = APIRouter()
api_router.include_router(documents_router)
api_router.include_router(query_router)
api_router.include_router(system_router)
api_router.include_router(evaluation_router)
api_router.include_router(reasoning_router)
api_router.include_router(temporal_router)
api_router.include_router(graph_router)
api_router.include_router(evidence_intelligence_router)
api_router.include_router(self_correction_router)
api_router.include_router(multimodal_router)
api_router.include_router(agent_router)
api_router.include_router(auth_router)
api_router.include_router(production_health_router)








