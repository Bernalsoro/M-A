"""
Data loading utilities for financial statements and news data.

Handles CSV and JSON file loading with proper validation and error handling.
"""

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from financial_rag_agent.config import settings

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads financial data from CSV and JSON sources."""

    def __init__(self, financials_path: Path | None = None, news_path: Path | None = None):
        """
        Initialize the data loader.

        Args:
            financials_path: Path to financial statements CSV
            news_path: Path to news/events JSON
        """
        self.financials_path = financials_path or settings.financials_path
        self.news_path = news_path or settings.news_path

    def load_financials(self) -> pd.DataFrame:
        """
        Load financial statements from CSV.

        Returns:
            DataFrame with financial data indexed by ticker and date

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        logger.info(f"Loading financial data from {self.financials_path}")

        if not self.financials_path.exists():
            raise FileNotFoundError(f"Financials file not found: {self.financials_path}")

        df = pd.read_csv(self.financials_path)

        # Validate required columns
        required_cols = [
            "ticker",
            "year",
            "quarter",
            "revenue",
            "net_income",
            "total_assets",
            "equity",
        ]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Convert numeric columns
        numeric_cols = [
            "revenue",
            "ebit",
            "net_income",
            "ebitda",
            "equity",
            "total_assets",
            "net_debt",
            "shares_outstanding",
            "operating_expenses",
            "cost_of_revenue",
            "cash_and_equivalents",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Create period identifier
        df["period"] = df["year"].astype(str) + "-" + df["quarter"]

        logger.info(f"Loaded {len(df)} financial records for {df['ticker'].nunique()} tickers")
        return df

    def load_news(self) -> list[dict[str, Any]]:
        """
        Load news and events from JSON.

        Returns:
            List of news items with ticker, date, headline, and summary

        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON structure is invalid
        """
        logger.info(f"Loading news data from {self.news_path}")

        if not self.news_path.exists():
            raise FileNotFoundError(f"News file not found: {self.news_path}")

        with open(self.news_path, "r", encoding="utf-8") as f:
            news_data = json.load(f)

        if not isinstance(news_data, list):
            raise ValueError("News JSON must be a list of objects")

        # Validate structure
        required_fields = {"ticker", "date", "headline", "summary"}
        for idx, item in enumerate(news_data):
            missing_fields = required_fields - set(item.keys())
            if missing_fields:
                raise ValueError(f"News item {idx} missing fields: {missing_fields}")

        logger.info(f"Loaded {len(news_data)} news items")
        return news_data

    def get_tickers(self) -> list[str]:
        """
        Get list of unique tickers from financial data.

        Returns:
            Sorted list of ticker symbols
        """
        df = self.load_financials()
        return sorted(df["ticker"].unique().tolist())

    def get_ticker_data(self, ticker: str) -> pd.DataFrame:
        """
        Get all financial data for a specific ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            DataFrame with financial data for the ticker, sorted by date

        Raises:
            ValueError: If ticker not found in data
        """
        df = self.load_financials()

        if ticker not in df["ticker"].values:
            available_tickers = df["ticker"].unique().tolist()
            raise ValueError(f"Ticker {ticker} not found. Available: {available_tickers}")

        ticker_df = df[df["ticker"] == ticker].copy()
        ticker_df = ticker_df.sort_values(["year", "quarter"], ascending=[False, False])

        return ticker_df

    def get_ticker_news(self, ticker: str) -> list[dict[str, Any]]:
        """
        Get all news items for a specific ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of news items for the ticker, sorted by date (newest first)
        """
        all_news = self.load_news()
        ticker_news = [item for item in all_news if item["ticker"] == ticker]

        # Sort by date descending
        ticker_news.sort(key=lambda x: x["date"], reverse=True)

        return ticker_news

    def get_latest_financials(self, ticker: str) -> dict[str, Any]:
        """
        Get the most recent financial data for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with latest financial metrics

        Raises:
            ValueError: If ticker not found
        """
        ticker_df = self.get_ticker_data(ticker)

        if ticker_df.empty:
            raise ValueError(f"No financial data found for {ticker}")

        # Get most recent period
        latest = ticker_df.iloc[0]

        return latest.to_dict()


# Convenience function for quick data loading
def load_all_data() -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Load all financial and news data.

    Returns:
        Tuple of (financials DataFrame, news list)
    """
    loader = DataLoader()
    financials = loader.load_financials()
    news = loader.load_news()
    return financials, news


if __name__ == "__main__":
    # CLI for testing data loading
    logging.basicConfig(level=logging.INFO)

    loader = DataLoader()

    print("Loading financial data...")
    financials = loader.load_financials()
    print(f"Loaded {len(financials)} records")
    print(f"\nTickers: {loader.get_tickers()}")

    print("\nLoading news data...")
    news = loader.load_news()
    print(f"Loaded {len(news)} news items")

    print("\nExample: Latest AAPL financials")
    aapl_latest = loader.get_latest_financials("AAPL")
    print(f"Revenue: ${aapl_latest['revenue']:,.0f}M")
    print(f"Net Income: ${aapl_latest['net_income']:,.0f}M")
    print(f"Period: {aapl_latest['period']}")
