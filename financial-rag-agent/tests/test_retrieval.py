"""
Tests for retrieval module (vector store and retriever).
"""

import pytest

from financial_rag_agent.ingestion.loader import DataLoader
from financial_rag_agent.retrieval.retriever import FinancialRetriever
from financial_rag_agent.retrieval.vector_store import VectorStore, build_vector_store_from_news


@pytest.fixture(scope="module")
def news_data():
    """Load news data for testing."""
    loader = DataLoader()
    return loader.load_news()


@pytest.fixture(scope="module")
def vector_store(news_data):
    """Create a vector store for testing."""
    # Build fresh vector store (don't save to avoid conflicts)
    vs = build_vector_store_from_news(news_data, save=False)
    return vs


@pytest.fixture
def retriever(vector_store):
    """Create a retriever instance."""
    return FinancialRetriever(vector_store=vector_store)


class TestVectorStore:
    """Tests for VectorStore class."""

    def test_vector_store_initialization(self):
        """Test vector store can be initialized."""
        vs = VectorStore()
        assert vs is not None
        assert vs.size == 0

    def test_add_documents(self, news_data):
        """Test adding documents to vector store."""
        vs = VectorStore()

        documents = [
            {"text": item["headline"] + " " + item["summary"], **item}
            for item in news_data[:5]
        ]

        vs.add_documents(documents, text_key="text")

        assert vs.size == 5
        assert len(vs.documents) == 5

    def test_vector_store_search(self, vector_store):
        """Test searching in vector store."""
        query = "What are the earnings results for Apple?"
        results = vector_store.search(query, top_k=3)

        assert len(results) <= 3
        assert all(isinstance(r, dict) for r in results)
        assert all("score" in r for r in results)

    def test_vector_store_search_relevance(self, vector_store):
        """Test that search returns relevant results."""
        query = "Apple iPhone sales"
        results = vector_store.search(query, top_k=5)

        # At least one result should be about AAPL
        ticker_counts = {}
        for r in results:
            ticker = r.get("ticker", "UNKNOWN")
            ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        # Should have at least one AAPL document in top results
        assert "AAPL" in ticker_counts

    def test_vector_store_empty_query(self, vector_store):
        """Test handling of empty query."""
        results = vector_store.search("", top_k=3)
        # Should still return results (based on empty embedding)
        assert isinstance(results, list)

    def test_vector_store_stats(self, vector_store):
        """Test getting vector store statistics."""
        stats = vector_store.get_stats()

        assert "num_documents" in stats
        assert "dimension" in stats
        assert "embedding_model" in stats
        assert stats["num_documents"] > 0


class TestFinancialRetriever:
    """Tests for FinancialRetriever class."""

    def test_retriever_initialization(self):
        """Test retriever can be initialized."""
        retriever = FinancialRetriever()
        assert retriever is not None

    def test_retrieve_for_ticker(self, retriever):
        """Test retrieval for specific ticker."""
        results = retriever.retrieve_for_ticker(
            ticker="AAPL",
            query="earnings performance",
            top_k=3,
        )

        assert isinstance(results, list)
        assert len(results) <= 3

        # Check that results are relevant to AAPL
        if results:
            # At least first result should be AAPL
            assert results[0].get("ticker") == "AAPL"

    def test_retrieve_for_comparison(self, retriever):
        """Test retrieval for ticker comparison."""
        results = retriever.retrieve_for_comparison(
            ticker1="AAPL",
            ticker2="MSFT",
            query="profitability and margins",
            top_k=2,
        )

        assert isinstance(results, dict)
        assert "AAPL" in results
        assert "MSFT" in results
        assert len(results["AAPL"]) <= 2
        assert len(results["MSFT"]) <= 2

    def test_retrieve_general(self, retriever):
        """Test general retrieval without ticker filter."""
        results = retriever.retrieve_general(
            query="AI and cloud computing growth",
            top_k=5,
        )

        assert isinstance(results, list)
        assert len(results) <= 5

    def test_format_context_for_llm(self, retriever):
        """Test formatting retrieved documents for LLM."""
        docs = [
            {
                "ticker": "AAPL",
                "date": "2024-11-02",
                "headline": "Apple beats earnings",
                "summary": "Strong quarter with revenue growth",
                "score": 0.95,
            }
        ]

        formatted = retriever.format_context_for_llm(docs)

        assert isinstance(formatted, str)
        assert "AAPL" in formatted
        assert "Apple beats earnings" in formatted
        assert "Strong quarter" in formatted

    def test_format_context_empty(self, retriever):
        """Test formatting empty document list."""
        formatted = retriever.format_context_for_llm([])
        assert "No relevant context found" in formatted

    def test_get_relevant_context(self, retriever):
        """Test main interface for getting context."""
        context = retriever.get_relevant_context(
            ticker="NVDA",
            query="GPU and AI business growth",
            top_k=3,
            format_for_llm=True,
        )

        assert isinstance(context, str)
        assert len(context) > 0


@pytest.mark.parametrize("ticker,query", [
    ("AAPL", "iPhone sales and revenue"),
    ("MSFT", "Azure and cloud services"),
    ("NVDA", "GPU demand and AI"),
    ("AMZN", "AWS and e-commerce"),
])
def test_retrieval_for_multiple_tickers(retriever, ticker, query):
    """Test retrieval works for various tickers and queries."""
    results = retriever.retrieve_for_ticker(ticker, query, top_k=3)

    assert isinstance(results, list)
    # Should get at least one result for known tickers
    assert len(results) >= 1
