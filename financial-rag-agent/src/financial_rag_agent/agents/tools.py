"""
Financial analysis tools for the agent.

Discrete actions the agent can take:
- Fetch financial data
- Compute financial ratios
- Retrieve textual context
- Compare tickers
"""

import logging
from typing import Any

from financial_rag_agent.ingestion.loader import DataLoader
from financial_rag_agent.ingestion.preprocessor import FinancialPreprocessor
from financial_rag_agent.retrieval.retriever import FinancialRetriever

logger = logging.getLogger(__name__)


class FinancialTools:
    """Collection of tools for financial analysis."""

    def __init__(self, loader: DataLoader | None = None, retriever: FinancialRetriever | None = None):
        """
        Initialize tools with required components.

        Args:
            loader: DataLoader instance (creates new one if not provided)
            retriever: FinancialRetriever instance (creates new one if not provided)
        """
        self.loader = loader or DataLoader()
        self.preprocessor = FinancialPreprocessor()
        self.retriever = retriever or FinancialRetriever()

        # Cache processed data to avoid recomputation
        self._processed_data = None

    def _get_processed_data(self):
        """Get or compute processed financial data with ratios."""
        if self._processed_data is None:
            df = self.loader.load_financials()
            self._processed_data = self.preprocessor.compute_all_ratios(df)
        return self._processed_data

    def fetch_financials(self, ticker: str) -> dict[str, Any]:
        """
        Fetch raw financial data for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with latest financial statement data

        Tool Description:
            Retrieves the most recent quarterly financial data including
            revenue, income, balance sheet items for the specified ticker.
        """
        logger.info(f"Tool: fetch_financials({ticker})")

        try:
            latest = self.loader.get_latest_financials(ticker)
            return {
                "tool": "fetch_financials",
                "ticker": ticker,
                "success": True,
                "data": latest,
            }
        except Exception as e:
            logger.error(f"Error fetching financials for {ticker}: {e}")
            return {"tool": "fetch_financials", "ticker": ticker, "success": False, "error": str(e)}

    def compute_ratios(self, ticker: str) -> dict[str, Any]:
        """
        Compute financial ratios and metrics for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with comprehensive ratio analysis

        Tool Description:
            Calculates key financial ratios including margins, returns (ROE, ROA),
            leverage metrics, growth rates, and per-share metrics.
        """
        logger.info(f"Tool: compute_ratios({ticker})")

        try:
            df = self._get_processed_data()
            summary = self.preprocessor.get_ticker_summary(df, ticker)

            return {
                "tool": "compute_ratios",
                "ticker": ticker,
                "success": True,
                "data": summary,
            }
        except Exception as e:
            logger.error(f"Error computing ratios for {ticker}: {e}")
            return {"tool": "compute_ratios", "ticker": ticker, "success": False, "error": str(e)}

    def retrieve_context(
        self, ticker: str, question: str, top_k: int = 5
    ) -> dict[str, Any]:
        """
        Retrieve relevant textual context (news, events) for a ticker.

        Args:
            ticker: Stock ticker symbol
            question: Query to guide retrieval
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with retrieved documents and formatted context

        Tool Description:
            Uses semantic search to find relevant news, earnings summaries,
            and other textual information related to the ticker and question.
        """
        logger.info(f"Tool: retrieve_context({ticker}, question='{question[:50]}...')")

        try:
            # Get raw documents
            documents = self.retriever.retrieve_for_ticker(ticker, question, top_k=top_k)

            # Format for LLM
            formatted_context = self.retriever.format_context_for_llm(documents)

            return {
                "tool": "retrieve_context",
                "ticker": ticker,
                "success": True,
                "documents": documents,
                "formatted_context": formatted_context,
                "num_docs": len(documents),
            }
        except Exception as e:
            logger.error(f"Error retrieving context for {ticker}: {e}")
            return {
                "tool": "retrieve_context",
                "ticker": ticker,
                "success": False,
                "error": str(e),
            }

    def compare_two_tickers(
        self, ticker1: str, ticker2: str, question: str | None = None
    ) -> dict[str, Any]:
        """
        Compare two tickers across key financial metrics.

        Args:
            ticker1: First ticker
            ticker2: Second ticker
            question: Optional question to guide comparison

        Returns:
            Dictionary with comparative analysis

        Tool Description:
            Performs side-by-side comparison of two companies including
            financial metrics (size, profitability, growth) and relevant news.
        """
        logger.info(f"Tool: compare_two_tickers({ticker1}, {ticker2})")

        try:
            df = self._get_processed_data()

            # Get financial comparison
            comparison = self.preprocessor.compare_tickers(df, ticker1, ticker2)

            # Get summaries for each ticker
            summary1 = self.preprocessor.get_ticker_summary(df, ticker1)
            summary2 = self.preprocessor.get_ticker_summary(df, ticker2)

            # Optionally retrieve context if question provided
            context_data = None
            if question:
                context_data = self.retriever.retrieve_for_comparison(
                    ticker1, ticker2, question, top_k=3
                )

            return {
                "tool": "compare_two_tickers",
                "ticker1": ticker1,
                "ticker2": ticker2,
                "success": True,
                "comparison": comparison,
                "summary1": summary1,
                "summary2": summary2,
                "context": context_data,
            }
        except Exception as e:
            logger.error(f"Error comparing {ticker1} and {ticker2}: {e}")
            return {
                "tool": "compare_two_tickers",
                "ticker1": ticker1,
                "ticker2": ticker2,
                "success": False,
                "error": str(e),
            }

    def get_available_tickers(self) -> dict[str, Any]:
        """
        Get list of available tickers in the dataset.

        Returns:
            Dictionary with list of tickers

        Tool Description:
            Returns all ticker symbols available in the financial database.
        """
        logger.info("Tool: get_available_tickers()")

        try:
            tickers = self.loader.get_tickers()
            return {
                "tool": "get_available_tickers",
                "success": True,
                "tickers": tickers,
                "count": len(tickers),
            }
        except Exception as e:
            logger.error(f"Error getting tickers: {e}")
            return {"tool": "get_available_tickers", "success": False, "error": str(e)}

    def get_ticker_news(self, ticker: str, limit: int = 5) -> dict[str, Any]:
        """
        Get recent news items for a ticker.

        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of news items

        Returns:
            Dictionary with news items

        Tool Description:
            Retrieves recent news, earnings announcements, and events
            for the specified ticker.
        """
        logger.info(f"Tool: get_ticker_news({ticker}, limit={limit})")

        try:
            news = self.loader.get_ticker_news(ticker)[:limit]

            return {
                "tool": "get_ticker_news",
                "ticker": ticker,
                "success": True,
                "news": news,
                "count": len(news),
            }
        except Exception as e:
            logger.error(f"Error getting news for {ticker}: {e}")
            return {"tool": "get_ticker_news", "ticker": ticker, "success": False, "error": str(e)}

    def get_tool_descriptions(self) -> dict[str, str]:
        """
        Get descriptions of all available tools.

        Returns:
            Dictionary mapping tool names to descriptions
        """
        tools = {
            "fetch_financials": "Fetch raw financial data (revenue, income, balance sheet)",
            "compute_ratios": "Calculate financial ratios (margins, ROE, leverage, growth)",
            "retrieve_context": "Search for relevant news and textual context",
            "compare_two_tickers": "Compare two companies side-by-side",
            "get_available_tickers": "List all available ticker symbols",
            "get_ticker_news": "Get recent news items for a ticker",
        }
        return tools


if __name__ == "__main__":
    # Test tools
    logging.basicConfig(level=logging.INFO)

    print("Testing Financial Tools\n" + "=" * 80)

    tools = FinancialTools()

    # Test 1: Fetch financials
    print("\n1. Fetch Financials (AAPL)")
    print("-" * 80)
    result = tools.fetch_financials("AAPL")
    if result["success"]:
        data = result["data"]
        print(f"Revenue: ${data['revenue']:,.0f}M")
        print(f"Net Income: ${data['net_income']:,.0f}M")
        print(f"Period: {data['period']}")

    # Test 2: Compute ratios
    print("\n2. Compute Ratios (AAPL)")
    print("-" * 80)
    result = tools.compute_ratios("AAPL")
    if result["success"]:
        data = result["data"]
        print(f"Net Margin: {data.get('net_margin', 'N/A'):.1f}%")
        print(f"ROE: {data.get('roe', 'N/A'):.1f}%")
        print(f"Revenue Growth: {data.get('revenue_growth_yoy', 'N/A'):.1f}%")

    # Test 3: Retrieve context
    print("\n3. Retrieve Context (AAPL)")
    print("-" * 80)
    result = tools.retrieve_context("AAPL", "recent earnings performance", top_k=2)
    if result["success"]:
        print(f"Retrieved {result['num_docs']} documents")
        print("\nFormatted Context Preview:")
        print(result["formatted_context"][:300] + "...")

    # Test 4: Compare tickers
    print("\n4. Compare Tickers (AAPL vs MSFT)")
    print("-" * 80)
    result = tools.compare_two_tickers("AAPL", "MSFT")
    if result["success"]:
        comp = result["comparison"]["comparison"]
        print(f"Revenue Ratio: {comp['revenue']['ratio']:.2f}x")
        print(f"Net Margin Diff: {comp['net_margin']['difference']:.2f}pp")
        print(f"ROE Diff: {comp['roe']['difference']:.2f}pp")

    # Test 5: Get available tickers
    print("\n5. Available Tickers")
    print("-" * 80)
    result = tools.get_available_tickers()
    if result["success"]:
        print(f"Available tickers ({result['count']}): {', '.join(result['tickers'])}")
