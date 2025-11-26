"""
High-level retrieval interface for financial context.

Combines vector search with filtering and ranking for optimal context retrieval.
"""

import logging
from typing import Any

from financial_rag_agent.config import settings
from financial_rag_agent.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)


class FinancialRetriever:
    """High-level interface for retrieving financial context."""

    def __init__(self, vector_store: VectorStore | None = None):
        """
        Initialize the retriever.

        Args:
            vector_store: Initialized VectorStore instance
        """
        self.vector_store = vector_store or VectorStore()

        # Try to load existing index
        if self.vector_store.size == 0:
            loaded = self.vector_store.load()
            if not loaded:
                logger.warning(
                    "No vector store found. Please run data ingestion first. "
                    "Use: python -m financial_rag_agent.ingestion.loader"
                )

    def retrieve_for_ticker(
        self,
        ticker: str,
        query: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context for a specific ticker.

        Args:
            ticker: Stock ticker symbol
            query: Query text
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score

        Returns:
            List of relevant documents with scores
        """
        top_k = top_k or settings.retrieval_top_k
        score_threshold = score_threshold or settings.retrieval_score_threshold

        # Enhance query with ticker for better matching
        enhanced_query = f"{ticker} {query}"

        # Search vector store
        all_results = self.vector_store.search(
            enhanced_query, top_k=top_k * 2, score_threshold=score_threshold
        )

        # Filter for specific ticker
        ticker_results = [doc for doc in all_results if doc.get("ticker") == ticker]

        # If not enough ticker-specific results, include general results
        if len(ticker_results) < top_k:
            ticker_results.extend(
                [doc for doc in all_results if doc.get("ticker") != ticker][
                    : top_k - len(ticker_results)
                ]
            )

        return ticker_results[:top_k]

    def retrieve_for_comparison(
        self,
        ticker1: str,
        ticker2: str,
        query: str,
        top_k: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Retrieve context for comparing two tickers.

        Args:
            ticker1: First ticker
            ticker2: Second ticker
            query: Query text
            top_k: Number of documents per ticker

        Returns:
            Dictionary with results for each ticker
        """
        top_k = top_k or settings.retrieval_top_k

        results1 = self.retrieve_for_ticker(ticker1, query, top_k=top_k)
        results2 = self.retrieve_for_ticker(ticker2, query, top_k=top_k)

        return {ticker1: results1, ticker2: results2}

    def retrieve_general(
        self, query: str, top_k: int | None = None, score_threshold: float | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant context without ticker filtering.

        Args:
            query: Query text
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score

        Returns:
            List of relevant documents
        """
        top_k = top_k or settings.retrieval_top_k
        score_threshold = score_threshold or settings.retrieval_score_threshold

        results = self.vector_store.search(query, top_k=top_k, score_threshold=score_threshold)
        return results

    def format_context_for_llm(self, documents: list[dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string for the LLM.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            ticker = doc.get("ticker", "N/A")
            date = doc.get("date", "N/A")
            headline = doc.get("headline", "")
            summary = doc.get("summary", doc.get("text", ""))

            context_part = f"""
Document {i}:
Ticker: {ticker}
Date: {date}
Headline: {headline}
Content: {summary}
"""
            context_parts.append(context_part.strip())

        context = "\n\n---\n\n".join(context_parts)
        return context

    def get_relevant_context(
        self,
        ticker: str | None,
        query: str,
        top_k: int | None = None,
        format_for_llm: bool = True,
    ) -> str | list[dict[str, Any]]:
        """
        Main interface: Get relevant context for a query.

        Args:
            ticker: Stock ticker (optional)
            query: Query text
            top_k: Number of documents
            format_for_llm: Whether to format as string for LLM

        Returns:
            Formatted context string or list of documents
        """
        if ticker:
            documents = self.retrieve_for_ticker(ticker, query, top_k=top_k)
        else:
            documents = self.retrieve_general(query, top_k=top_k)

        if format_for_llm:
            return self.format_context_for_llm(documents)
        else:
            return documents

    def get_vector_store_info(self) -> dict[str, Any]:
        """
        Get information about the vector store.

        Returns:
            Dictionary with vector store statistics
        """
        return self.vector_store.get_stats()


if __name__ == "__main__":
    # Test retriever
    logging.basicConfig(level=logging.INFO)

    retriever = FinancialRetriever()

    # Test 1: Single ticker query
    print("=" * 80)
    print("Test 1: Retrieve context for AAPL")
    print("=" * 80)

    query = "What are the recent earnings results and growth outlook?"
    context = retriever.get_relevant_context("AAPL", query, top_k=3)
    print(context)

    # Test 2: Comparison query
    print("\n" + "=" * 80)
    print("Test 2: Comparison query (AAPL vs MSFT)")
    print("=" * 80)

    query = "Cloud and AI business performance"
    comparison = retriever.retrieve_for_comparison("AAPL", "MSFT", query, top_k=2)

    print("\nAAPL context:")
    print(retriever.format_context_for_llm(comparison["AAPL"]))

    print("\nMSFT context:")
    print(retriever.format_context_for_llm(comparison["MSFT"]))

    # Test 3: General query
    print("\n" + "=" * 80)
    print("Test 3: General query across all tickers")
    print("=" * 80)

    query = "Which companies are investing heavily in AI infrastructure?"
    context = retriever.get_relevant_context(None, query, top_k=5)
    print(context)

    # Print vector store info
    print("\n" + "=" * 80)
    print("Vector Store Info:")
    print("=" * 80)
    info = retriever.get_vector_store_info()
    for key, value in info.items():
        print(f"{key}: {value}")
