"""
Retrieval Benchmark Engine evaluating Pure Dense, Pure BM25, Hybrid RRF, and Cross-Encoder Reranker.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import time
from app.domain.models import (
    RetrievalMode,
    BenchmarkReport,
    MethodBenchmarkResult,
    EvaluationMetricScores
)
from app.domain.models import Document, DocumentMetadata
from app.infrastructure.chunking.semantic_chunker import SemanticChunker
from app.infrastructure.embeddings.embedder import get_embedder
from app.infrastructure.retrieval.vector_store import DenseVectorStore
from app.infrastructure.retrieval.keyword_store import BM25KeywordStore
from app.services.retrieval_service import RetrievalService
from app.evaluation.metrics import RetrievalMetrics
from app.core.logging import logger


class RetrievalBenchmarkRunner:
    """Executes multi-method comparative evaluations against benchmark datasets."""

    def __init__(self, dataset_path: Optional[Path] = None):
        self.dataset_path = dataset_path or (Path(__file__).parent / "datasets" / "sample_eval_data.json")

    def run_benchmark(self) -> BenchmarkReport:
        logger.info(f"Starting retrieval benchmark with dataset from {self.dataset_path}")
        
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        test_corpus = data.get("test_corpus", [])
        test_queries = data.get("test_queries", [])

        # Create isolated temporary in-memory retrieval environment
        chunker = SemanticChunker(chunk_size=400, chunk_overlap=80)
        embedder = get_embedder()
        v_store = DenseVectorStore(storage_path=Path("backend/data/indices/_eval_temp.json"))
        k_store = BM25KeywordStore()

        # Ingest benchmark corpus
        all_chunks = []
        for item in test_corpus:
            doc = Document(
                id=item["id"],
                filename=item["filename"],
                content=item["content"],
                metadata=DocumentMetadata(
                    title=item["filename"],
                    file_type="md",
                    file_size=len(item["content"])
                )
            )
            chunks = chunker.chunk(doc)
            texts = [c.content for c in chunks]
            embs = embedder.embed_texts(texts)
            for idx, c in enumerate(chunks):
                c.embedding = embs[idx]
            all_chunks.extend(chunks)

        v_store.add_chunks(all_chunks)
        k_store.index_chunks(all_chunks)

        service = RetrievalService(vector_store=v_store, keyword_store=k_store)

        # Define 4 benchmark configurations
        methods = {
            "pure_dense_vector": {
                "desc": "Dense Semantic Embeddings with Cosine Similarity (Vector Only)",
                "mode": RetrievalMode(use_dense=True, use_sparse=False, use_reranker=False, top_k=10)
            },
            "pure_sparse_bm25": {
                "desc": "BM25 Okapi Lexical Keyword Search (BM25 Only)",
                "mode": RetrievalMode(use_dense=False, use_sparse=True, use_reranker=False, top_k=10)
            },
            "hybrid_rrf": {
                "desc": "Hybrid Dense + BM25 with Reciprocal Rank Fusion (k=60)",
                "mode": RetrievalMode(use_dense=True, use_sparse=True, use_reranker=False, dense_weight=0.6, sparse_weight=0.4, top_k=10)
            },
            "hybrid_cross_encoder": {
                "desc": "Hybrid RRF (Top 50) + Neural Cross-Encoder Reranker (Top 10)",
                "mode": RetrievalMode(use_dense=True, use_sparse=True, use_reranker=True, dense_weight=0.6, sparse_weight=0.4, top_k=50, rerank_top_k=10)
            }
        }

        method_results: Dict[str, MethodBenchmarkResult] = {}

        for m_key, m_info in methods.items():
            mode = m_info["mode"]
            latencies = []
            
            all_metrics: List[EvaluationMetricScores] = []

            for q_item in test_queries:
                q_text = q_item["query"]
                target_filename = list(q_item.get("relevance_grades", {}).keys())[0] if q_item.get("relevance_grades") else ""

                t0 = time.time()
                results = service.retrieve(query=q_text, mode=mode)
                latencies.append((time.time() - t0) * 1000)

                # Ground truth chunk IDs (chunks originating from the target filename)
                ground_truth_ids = {c.id for c in all_chunks if target_filename.lower() in c.metadata.get("filename", "").lower()}
                retrieved_ids = [r.chunk.id for r in results]
                
                rel_map = {cid: 3.0 for cid in ground_truth_ids}
                scores = RetrievalMetrics.compute_all(retrieved_ids, ground_truth_ids, rel_map)
                all_metrics.append(scores)

            # Average metrics across all queries
            num_q = len(test_queries) or 1
            avg_scores = EvaluationMetricScores(
                recall_at_1=round(sum(m.recall_at_1 for m in all_metrics) / num_q, 4),
                recall_at_3=round(sum(m.recall_at_3 for m in all_metrics) / num_q, 4),
                recall_at_5=round(sum(m.recall_at_5 for m in all_metrics) / num_q, 4),
                recall_at_10=round(sum(m.recall_at_10 for m in all_metrics) / num_q, 4),
                precision_at_1=round(sum(m.precision_at_1 for m in all_metrics) / num_q, 4),
                precision_at_3=round(sum(m.precision_at_3 for m in all_metrics) / num_q, 4),
                precision_at_5=round(sum(m.precision_at_5 for m in all_metrics) / num_q, 4),
                precision_at_10=round(sum(m.precision_at_10 for m in all_metrics) / num_q, 4),
                mrr=round(sum(m.mrr for m in all_metrics) / num_q, 4),
                ndcg_at_5=round(sum(m.ndcg_at_5 for m in all_metrics) / num_q, 4),
                ndcg_at_10=round(sum(m.ndcg_at_10 for m in all_metrics) / num_q, 4),
            )

            avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

            method_results[m_key] = MethodBenchmarkResult(
                method_name=m_key,
                description=m_info["desc"],
                metrics=avg_scores,
                average_latency_ms=avg_lat
            )

        # Calculate Superiority Delta (Hybrid+Reranker vs Pure Vector)
        pure_vec_mrr = method_results["pure_dense_vector"].metrics.mrr
        hybrid_mrr = method_results["hybrid_cross_encoder"].metrics.mrr
        mrr_lift = round(((hybrid_mrr - pure_vec_mrr) / max(pure_vec_mrr, 0.01)) * 100, 1)

        pure_vec_recall = method_results["pure_dense_vector"].metrics.recall_at_5
        hybrid_recall = method_results["hybrid_cross_encoder"].metrics.recall_at_5
        recall_lift = round(((hybrid_recall - pure_vec_recall) / max(pure_vec_recall, 0.01)) * 100, 1)

        # Cleanup temp eval file
        try:
            temp_p = Path("backend/data/indices/_eval_temp.json")
            if temp_p.exists():
                temp_p.unlink()
        except Exception:
            pass

        report = BenchmarkReport(
            benchmark_timestamp=datetime.utcnow().isoformat(),
            total_test_queries=len(test_queries),
            corpus_documents_count=len(test_corpus),
            corpus_chunks_count=len(all_chunks),
            results_by_method=method_results,
            hybrid_superiority_delta={
                "mrr_relative_lift_percent": mrr_lift,
                "recall_at_5_lift_percent": recall_lift,
                "ndcg_at_10_delta": round(method_results["hybrid_cross_encoder"].metrics.ndcg_at_10 - method_results["pure_dense_vector"].metrics.ndcg_at_10, 4)
            }
        )

        logger.info(f"Benchmark completed: MRR Lift={mrr_lift}%, Recall@5 Lift={recall_lift}%")
        return report
