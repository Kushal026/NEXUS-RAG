"""
Evidence Service synthesizing search results into structured evidence packages with claim-level citations.
"""
from typing import Optional
from app.domain.models import (
    RetrievalMode,
    EvidenceSynthesisResult
)
from app.services.retrieval_service import RetrievalService
from app.infrastructure.llm.provider import get_llm_provider
from app.core.logging import logger


class EvidenceService:
    """Coordinates retrieval and LLM evidence synthesis."""

    def __init__(self, retrieval_service: Optional[RetrievalService] = None):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.llm_provider = get_llm_provider()

    def synthesize_evidence(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None
    ) -> EvidenceSynthesisResult:
        logger.info(f"Synthesizing evidence for query: '{query}'")
        
        # 1. Retrieve ranked evidence chunks with full observability trace
        evidence_chunks, trace = self.retrieval_service.retrieve_with_trace(query=query, mode=mode)

        # 2. Synthesize answer with claim citations and verification
        result = self.llm_provider.generate_synthesis(
            query=query,
            evidence_chunks=evidence_chunks
        )
        result.retrieval_trace = trace

        return result

    async def synthesize_evidence_stream(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None
    ):
        """Streams evidence synthesis tokens and final structured metadata over SSE."""
        import asyncio
        import json

        # 1. Retrieve ranked evidence chunks with full trace
        evidence_chunks, trace = self.retrieval_service.retrieve_with_trace(query=query, mode=mode)
        
        # 2. Generate full structured result
        full_result = self.llm_provider.generate_synthesis(
            query=query,
            evidence_chunks=evidence_chunks
        )
        full_result.retrieval_trace = trace

        # Stream chunk tokens simulating real-time LLM token generation
        words = full_result.synthesis_markdown.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            event_data = {"event": "token", "data": token}
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(0.01)

        # Send final metadata event with full trace
        final_data = {
            "event": "done",
            "result": full_result.model_dump()
        }
        yield f"data: {json.dumps(final_data)}\n\n"


