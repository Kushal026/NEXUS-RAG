"""
Unit tests for Information Retrieval Evaluation Metrics and Benchmark Execution.
"""
from app.evaluation.metrics import RetrievalMetrics
from app.evaluation.benchmark import RetrievalBenchmarkRunner


def test_retrieval_metrics_calculations():
    retrieved = ["doc_a", "doc_b", "doc_c", "doc_d", "doc_e"]
    ground_truth = {"doc_a", "doc_c"}
    rel_map = {"doc_a": 3.0, "doc_c": 2.0}

    # Recall & Precision
    recall_1 = RetrievalMetrics.recall_at_k(retrieved, ground_truth, 1)
    recall_3 = RetrievalMetrics.recall_at_k(retrieved, ground_truth, 3)
    prec_1 = RetrievalMetrics.precision_at_k(retrieved, ground_truth, 1)

    assert recall_1 == 0.5  # 1 out of 2 ground truth
    assert recall_3 == 1.0  # both doc_a and doc_c found
    assert prec_1 == 1.0

    # MRR (doc_a is at rank 1)
    mrr = RetrievalMetrics.mean_reciprocal_rank(retrieved, ground_truth)
    assert mrr == 1.0

    # NDCG
    ndcg = RetrievalMetrics.ndcg_at_k(retrieved, rel_map, 5)
    assert 0.0 < ndcg <= 1.0


def test_benchmark_runner_execution():
    runner = RetrievalBenchmarkRunner()
    report = runner.run_benchmark()

    assert report.total_test_queries >= 1
    assert "pure_dense_vector" in report.results_by_method
    assert "pure_sparse_bm25" in report.results_by_method
    assert "hybrid_cross_encoder" in report.results_by_method

    # Verify hybrid has high recall and valid latency
    hybrid_res = report.results_by_method["hybrid_cross_encoder"]
    assert hybrid_res.metrics.recall_at_5 > 0.0
    assert hybrid_res.average_latency_ms >= 0.0
