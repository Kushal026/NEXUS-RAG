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

api_router = APIRouter()
api_router.include_router(documents_router)
api_router.include_router(query_router)
api_router.include_router(system_router)
api_router.include_router(evaluation_router)
api_router.include_router(reasoning_router)
api_router.include_router(temporal_router)
api_router.include_router(graph_router)



