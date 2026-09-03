"""
Unit tests for Query Understanding and Intent Analysis.
"""
from app.infrastructure.query_understanding.query_analyzer import QueryAnalyzer


def test_query_analyzer_intent_and_entities():
    analyzer = QueryAnalyzer()
    
    # Technical query with alphanumeric entity
    res = analyzer.analyze("What is the operating temperature of NEXUS-7700-TX cryogenic controller?")
    assert "NEXUS-7700-TX" in res.entities
    assert res.suggested_retrieval_mode == "hybrid_boost_bm25"
    assert "temperature" in res.keywords
    assert "cryogenic" in res.keywords


def test_query_analyzer_comparative_intent():
    analyzer = QueryAnalyzer()
    res = analyzer.analyze("Compare dense vector search versus BM25 lexical retrieval")
    assert res.intent == "comparative_analysis"
    assert "BM25" in res.entities


def test_query_analyzer_constraint_extraction():
    analyzer = QueryAnalyzer()
    res = analyzer.analyze("doc:specs.pdf author:Smith after:2023 quantum entanglement")
    assert "specs.pdf" in res.constraints.target_documents
    assert "Smith" in res.constraints.target_authors
    assert res.constraints.date_after == "2023"
    assert "doc:specs.pdf" not in res.cleaned_query
    assert "quantum" in res.keywords
