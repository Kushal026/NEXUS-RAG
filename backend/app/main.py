"""
FastAPI application entrypoint for NEXUS-RAG.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.v1.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.PROJECT_NAME} API",
        version=settings.VERSION,
        description="Neural Evidence & eXplainability Unified Search - Backend Engine",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes under /api/v1 and root
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    app.include_router(api_router, prefix="")

    @app.get("/health")
    async def root_health():
        return {"status": "ok", "service": settings.PROJECT_NAME, "version": settings.VERSION}

    @app.get("/")
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs"
        }

    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} initialized successfully.")
    return app


app = create_app()
