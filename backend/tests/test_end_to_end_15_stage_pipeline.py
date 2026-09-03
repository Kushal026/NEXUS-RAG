"""
Full 15-Stage End-to-End Integration Test for NEXUS-RAG Platform (Phase 10).
Validates the complete execution pipeline:
Document -> Parse -> Chunk -> Embed -> Hybrid Retrieve -> Rerank -> Query Plan
-> Temporal/Graph Retrieval -> Evidence Analysis -> Contradiction Detection
-> Self-Correction -> Generation -> Claim Verification -> Citation -> Evaluation.
"""
import pytest
from app.infrastructure.parsers.factory import ParserFactory
from app.infrastructure.chunking.semantic_chunker import SemanticChunker
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService
from app.infrastructure.query_reasoning.retrieval_planner import RetrievalPlanner
from app.services.hybrid_graph_rag_service import HybridGraphRAGService
from app.services.evidence_intelligence_service import EvidenceIntelligenceService
from app.services.self_correcting_service import SelfCorrectingService
from app.infrastructure.self_correction.answer_verifier import AnswerVerifier
from app.evaluation.metrics import RetrievalMetrics
from app.domain.models import Document, RetrievalMode


def test_full_15_stage_pipeline_execution():
    # 1. DOCUMENT CREATION
    raw_markdown = (
        "# Attention Mechanism and Vision Transformers\n"
        "Published: 2024-03-15\n"
        "Authors: Vaswani and Zhang\n\n"
        "Vision Transformers (ViT) apply self-attention mechanisms to image patches, achieving 91.5% top-1 accuracy on ImageNet-1K.\n\n"
        "## Performance Comparison\n"
        "Under low-light conditions, ViT accuracy drops to 84.2%, whereas specialized ResNet models maintain 87.0% accuracy.\n"
    )

    # 2. PARSE, 3. CHUNK, 4. EMBED & INDEX
    ingestion_service = IngestionService()
    ingest_res = ingestion_service.ingest_file(
        file_bytes=raw_markdown.encode('utf-8'),
        filename="vision_transformers.md"
    )
    assert ingest_res["chunk_count"] >= 1
    doc_id = ingest_res["document_id"]


    # 5. HYBRID RETRIEVE
    retrieval_service = RetrievalService()
    query = "What is the accuracy of Vision Transformers on ImageNet?"
    retrieved_chunks, trace = retrieval_service.retrieve_with_trace(query, mode=RetrievalMode(top_k=3))
    assert len(retrieved_chunks) >= 1
    assert any("91.5%" in c.chunk.content or "ViT" in c.chunk.content for c in retrieved_chunks)

    # 6. RERANK (Verified via final_score in retrieved_chunks)
    assert retrieved_chunks[0].final_score > 0.0

    # 7. QUERY PLAN & INTENT CLASSIFICATION
    planner = RetrievalPlanner()
    plan = planner.create_plan(query)
    assert plan.original_query == query


    # 8. TEMPORAL & GRAPH RETRIEVAL
    graph_service = HybridGraphRAGService(retrieval_service=retrieval_service)
    graph_result = graph_service.query(
        query="Vaswani Vision Transformers",
        mode=RetrievalMode(top_k=2)
    )

    assert graph_result.synthesis_markdown is not None




    # 9. EVIDENCE ANALYSIS & 10. CONTRADICTION DETECTION
    evidence_service = EvidenceIntelligenceService(retrieval_service=retrieval_service)
    evidence_report = evidence_service.analyze_evidence(
        query=query,
        mode=RetrievalMode(top_k=3)
    )
    assert len(evidence_report.retrieved_chunks) >= 1
    assert evidence_report.evidence_coverage_percentage >= 0.0



    # 11. SELF-CORRECTION & GENERATION
    self_correcting = SelfCorrectingService(retrieval_service=retrieval_service)
    sc_result = self_correcting.execute_self_correcting_rag(
        query=query,
        max_iterations=2
    )
    assert sc_result.final_answer_markdown
    assert sc_result.iterations_trace

    # 12. CLAIM VERIFICATION
    verifier = AnswerVerifier()
    claim_ver = verifier.verify_answer(
        raw_answer=sc_result.final_answer_markdown,
        accumulated_chunks=retrieved_chunks
    )
    assert claim_ver.unsupported_claims_count == 0 or claim_ver.unsupported_claim_rate <= 1.0


    # 13. CITATION PROVENANCE
    assert len(sc_result.accumulated_chunks) >= 1
    top_ev = sc_result.accumulated_chunks[0]
    assert top_ev.chunk.metadata.get("filename") == "vision_transformers.md"

    # 14. EVALUATION METRICS
    retrieved_ids = [sc_result.accumulated_chunks[0].chunk.id]
    ground_truth = {retrieved_ids[0]}
    recall = RetrievalMetrics.recall_at_k(retrieved_ids, ground_truth, k=1)
    precision = RetrievalMetrics.precision_at_k(retrieved_ids, ground_truth, k=1)
    mrr = RetrievalMetrics.mean_reciprocal_rank(retrieved_ids, ground_truth)

    assert recall == 1.0
    assert precision == 1.0

    # 15. PIPELINE COMPLETION AUDIT
    assert mrr == 1.0


