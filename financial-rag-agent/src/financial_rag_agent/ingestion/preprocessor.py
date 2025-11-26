"""
Financial data preprocessing and ratio computation.

Calculates key financial metrics used in equity analysis:
- Profitability ratios (margins, ROE, ROA)
- Growth metrics (YoY revenue, earnings growth)
- Leverage metrics (debt/equity, coverage ratios)
- Valuation inputs (EPS, book value per share)
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class FinancialPreprocessor:
    """Computes financial ratios and derived metrics."""

    @staticmethod
    def compute_margins(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profit margins.

        Args:
            df: DataFrame with revenue, ebit, net_income, ebitda

        Returns:
            DataFrame with added margin columns
        """
        df = df.copy()

        if "revenue" in df.columns and df["revenue"].notna().any():
            # Gross margin (requires cost_of_revenue)
            if "cost_of_revenue" in df.columns:
                df["gross_margin"] = (
                    (df["revenue"] - df["cost_of_revenue"]) / df["revenue"] * 100
                )

            # Operating margin (EBIT margin)
            if "ebit" in df.columns:
                df["operating_margin"] = df["ebit"] / df["revenue"] * 100

            # EBITDA margin
            if "ebitda" in df.columns:
                df["ebitda_margin"] = df["ebitda"] / df["revenue"] * 100

            # Net margin
            if "net_income" in df.columns:
                df["net_margin"] = df["net_income"] / df["revenue"] * 100

        return df

    @staticmethod
    def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate return ratios (ROE, ROA, ROIC).

        Args:
            df: DataFrame with net_income, equity, total_assets

        Returns:
            DataFrame with added return columns
        """
        df = df.copy()

        # ROE (Return on Equity)
        if "net_income" in df.columns and "equity" in df.columns:
            df["roe"] = df["net_income"] / df["equity"] * 100

        # ROA (Return on Assets)
        if "net_income" in df.columns and "total_assets" in df.columns:
            df["roa"] = df["net_income"] / df["total_assets"] * 100

        # ROIC approximation (EBIT / Invested Capital)
        # Invested Capital ≈ Equity + Net Debt
        if "ebit" in df.columns and "equity" in df.columns and "net_debt" in df.columns:
            invested_capital = df["equity"] + df["net_debt"]
            df["roic"] = df["ebit"] / invested_capital * 100

        return df

    @staticmethod
    def compute_leverage(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate leverage metrics.

        Args:
            df: DataFrame with total_assets, equity, net_debt, ebitda

        Returns:
            DataFrame with added leverage columns
        """
        df = df.copy()

        # Debt-to-Equity ratio
        if "net_debt" in df.columns and "equity" in df.columns:
            df["debt_to_equity"] = df["net_debt"] / df["equity"]

        # Net Debt / EBITDA (leverage multiple)
        if "net_debt" in df.columns and "ebitda" in df.columns:
            df["net_debt_to_ebitda"] = df["net_debt"] / df["ebitda"]

        # Equity ratio (equity / total assets)
        if "equity" in df.columns and "total_assets" in df.columns:
            df["equity_ratio"] = df["equity"] / df["total_assets"] * 100

        return df

    @staticmethod
    def compute_per_share_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate per-share metrics.

        Args:
            df: DataFrame with shares_outstanding and various financial metrics

        Returns:
            DataFrame with added per-share columns
        """
        df = df.copy()

        if "shares_outstanding" not in df.columns:
            return df

        # EPS (Earnings Per Share)
        if "net_income" in df.columns:
            df["eps"] = df["net_income"] / df["shares_outstanding"]

        # Book Value Per Share
        if "equity" in df.columns:
            df["book_value_per_share"] = df["equity"] / df["shares_outstanding"]

        # Revenue Per Share
        if "revenue" in df.columns:
            df["revenue_per_share"] = df["revenue"] / df["shares_outstanding"]

        return df

    @staticmethod
    def compute_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate YoY growth rates.

        Assumes df is sorted by period with most recent first.

        Args:
            df: DataFrame sorted by date (descending)

        Returns:
            DataFrame with added growth rate columns
        """
        df = df.copy()
        df = df.sort_values(["year", "quarter"], ascending=[False, False]).reset_index(drop=True)

        growth_cols = ["revenue", "ebit", "net_income", "ebitda"]

        for col in growth_cols:
            if col in df.columns:
                growth_col_name = f"{col}_growth_yoy"
                # Calculate YoY growth (assumes quarterly data, so look back 4 periods)
                if len(df) >= 5:
                    df[growth_col_name] = (
                        (df[col] - df[col].shift(-4)) / df[col].shift(-4) * 100
                    )
                else:
                    # Sequential growth if not enough data
                    df[growth_col_name] = (df[col] - df[col].shift(-1)) / df[col].shift(-1) * 100

        return df

    def compute_all_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all financial ratios and metrics.

        Args:
            df: Raw financial DataFrame

        Returns:
            DataFrame with all computed ratios
        """
        logger.info("Computing financial ratios...")

        df = self.compute_margins(df)
        df = self.compute_returns(df)
        df = self.compute_leverage(df)
        df = self.compute_per_share_metrics(df)
        df = self.compute_growth_rates(df)

        logger.info("Ratio computation complete")
        return df

    def get_ticker_summary(self, df: pd.DataFrame, ticker: str) -> dict[str, Any]:
        """
        Get comprehensive financial summary for a ticker.

        Args:
            df: DataFrame with computed ratios (all tickers)
            ticker: Stock ticker symbol

        Returns:
            Dictionary with latest metrics and ratios

        Raises:
            ValueError: If ticker not found
        """
        ticker_df = df[df["ticker"] == ticker].copy()

        if ticker_df.empty:
            raise ValueError(f"Ticker {ticker} not found in data")

        # Sort by period (most recent first)
        ticker_df = ticker_df.sort_values(["year", "quarter"], ascending=[False, False])

        latest = ticker_df.iloc[0].to_dict()

        # Format summary
        summary = {
            "ticker": ticker,
            "period": latest.get("period", f"{latest.get('year')}-{latest.get('quarter')}"),
            "sector": latest.get("sector", "N/A"),
            # Core metrics
            "revenue": latest.get("revenue"),
            "net_income": latest.get("net_income"),
            "ebitda": latest.get("ebitda"),
            "equity": latest.get("equity"),
            "total_assets": latest.get("total_assets"),
            "net_debt": latest.get("net_debt"),
            # Margins
            "gross_margin": latest.get("gross_margin"),
            "operating_margin": latest.get("operating_margin"),
            "ebitda_margin": latest.get("ebitda_margin"),
            "net_margin": latest.get("net_margin"),
            # Returns
            "roe": latest.get("roe"),
            "roa": latest.get("roa"),
            "roic": latest.get("roic"),
            # Leverage
            "debt_to_equity": latest.get("debt_to_equity"),
            "net_debt_to_ebitda": latest.get("net_debt_to_ebitda"),
            "equity_ratio": latest.get("equity_ratio"),
            # Per share
            "eps": latest.get("eps"),
            "book_value_per_share": latest.get("book_value_per_share"),
            # Growth
            "revenue_growth_yoy": latest.get("revenue_growth_yoy"),
            "net_income_growth_yoy": latest.get("net_income_growth_yoy"),
        }

        return summary

    def compare_tickers(
        self, df: pd.DataFrame, ticker1: str, ticker2: str
    ) -> dict[str, Any]:
        """
        Compare key metrics between two tickers.

        Args:
            df: DataFrame with computed ratios
            ticker1: First ticker
            ticker2: Second ticker

        Returns:
            Dictionary with comparison data

        Raises:
            ValueError: If either ticker not found
        """
        summary1 = self.get_ticker_summary(df, ticker1)
        summary2 = self.get_ticker_summary(df, ticker2)

        comparison = {
            "ticker1": ticker1,
            "ticker2": ticker2,
            "comparison": {
                "revenue": {
                    ticker1: summary1["revenue"],
                    ticker2: summary2["revenue"],
                    "ratio": summary1["revenue"] / summary2["revenue"]
                    if summary2["revenue"]
                    else None,
                },
                "net_margin": {
                    ticker1: summary1.get("net_margin"),
                    ticker2: summary2.get("net_margin"),
                    "difference": summary1.get("net_margin", 0) - summary2.get("net_margin", 0),
                },
                "roe": {
                    ticker1: summary1.get("roe"),
                    ticker2: summary2.get("roe"),
                    "difference": summary1.get("roe", 0) - summary2.get("roe", 0),
                },
                "debt_to_equity": {
                    ticker1: summary1.get("debt_to_equity"),
                    ticker2: summary2.get("debt_to_equity"),
                },
                "revenue_growth": {
                    ticker1: summary1.get("revenue_growth_yoy"),
                    ticker2: summary2.get("revenue_growth_yoy"),
                },
            },
        }

        return comparison


if __name__ == "__main__":
    # Test preprocessing
    logging.basicConfig(level=logging.INFO)

    from financial_rag_agent.ingestion.loader import DataLoader

    loader = DataLoader()
    df = loader.load_financials()

    preprocessor = FinancialPreprocessor()
    df_processed = preprocessor.compute_all_ratios(df)

    print("Processed DataFrame columns:")
    print(df_processed.columns.tolist())

    print("\nAAPL Summary:")
    aapl_summary = preprocessor.get_ticker_summary(df_processed, "AAPL")
    for key, value in aapl_summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    print("\nAAPL vs MSFT Comparison:")
    comparison = preprocessor.compare_tickers(df_processed, "AAPL", "MSFT")
    print(f"Revenue Ratio: {comparison['comparison']['revenue']['ratio']:.2f}x")
    print(
        f"Net Margin Difference: {comparison['comparison']['net_margin']['difference']:.2f}pp"
    )
