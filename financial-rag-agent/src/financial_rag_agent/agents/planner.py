"""
Agent planner for task decomposition and tool selection.

Analyzes user questions and decides:
- Question type (single ticker, comparison, general market)
- Required tools and execution order
- Query strategy
"""

import logging
import re
from typing import Any, Literal

logger = logging.getLogger(__name__)


class AgentPlanner:
    """Plans agent actions based on user questions."""

    # Keywords for detecting question types
    COMPARISON_KEYWORDS = [
        "compare",
        "versus",
        "vs",
        "vs.",
        "compared to",
        "difference between",
        "better than",
        "worse than",
    ]

    RISK_KEYWORDS = [
        "risk",
        "risks",
        "threat",
        "threats",
        "concern",
        "concerns",
        "vulnerability",
        "weakness",
        "challenge",
        "challenges",
    ]

    GROWTH_KEYWORDS = [
        "growth",
        "growing",
        "expansion",
        "increase",
        "trend",
        "momentum",
        "outlook",
    ]

    PROFITABILITY_KEYWORDS = [
        "profit",
        "margin",
        "margins",
        "profitability",
        "earnings",
        "income",
        "roe",
        "roa",
        "return",
    ]

    VALUATION_KEYWORDS = [
        "valuation",
        "value",
        "valued",
        "price",
        "expensive",
        "cheap",
        "multiple",
        "multiples",
        "eps",
        "pe",
    ]

    def __init__(self):
        """Initialize the planner."""
        pass

    def extract_tickers(self, question: str, ticker_hint: str | None = None) -> list[str]:
        """
        Extract ticker symbols from question or use provided hint.

        Args:
            question: User question
            ticker_hint: Optional ticker provided separately

        Returns:
            List of extracted tickers
        """
        tickers = []

        # If explicit ticker provided, use it
        if ticker_hint:
            tickers.append(ticker_hint.upper())

        # Look for ticker patterns in question (uppercase 2-5 letter words)
        ticker_pattern = r"\b([A-Z]{2,5})\b"
        matches = re.findall(ticker_pattern, question)

        # Common tickers
        known_tickers = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "GOOG",
            "AMZN",
            "META",
            "NVDA",
            "TSLA",
            "BRK",
            "JPM",
        ]

        for match in matches:
            if match in known_tickers and match not in tickers:
                tickers.append(match)

        # Also look for company names
        company_map = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "meta": "META",
            "facebook": "META",
            "nvidia": "NVDA",
            "tesla": "TSLA",
        }

        question_lower = question.lower()
        for company, ticker in company_map.items():
            if company in question_lower and ticker not in tickers:
                tickers.append(ticker)

        return tickers

    def classify_question_type(
        self, question: str, tickers: list[str]
    ) -> Literal["single_ticker", "comparison", "risk_analysis", "general"]:
        """
        Classify the type of question.

        Args:
            question: User question
            tickers: Extracted tickers

        Returns:
            Question type
        """
        question_lower = question.lower()

        # Check for comparison
        if len(tickers) >= 2:
            return "comparison"

        for keyword in self.COMPARISON_KEYWORDS:
            if keyword in question_lower:
                return "comparison"

        # Check for risk analysis
        for keyword in self.RISK_KEYWORDS:
            if keyword in question_lower:
                return "risk_analysis"

        # Single ticker or general
        if len(tickers) == 1:
            return "single_ticker"

        return "general"

    def determine_tools_needed(
        self, question: str, question_type: str, tickers: list[str]
    ) -> list[str]:
        """
        Determine which tools are needed to answer the question.

        Args:
            question: User question
            question_type: Classified question type
            tickers: Extracted tickers

        Returns:
            Ordered list of tool names
        """
        tools = []
        question_lower = question.lower()

        # For single ticker analysis
        if question_type == "single_ticker":
            # Always compute ratios for single ticker
            tools.append("compute_ratios")

            # Check if we need context/news
            needs_context = (
                "recent" in question_lower
                or "news" in question_lower
                or "earnings" in question_lower
                or "outlook" in question_lower
                or "event" in question_lower
                or any(kw in question_lower for kw in self.GROWTH_KEYWORDS)
            )

            if needs_context:
                tools.append("retrieve_context")

        # For comparison
        elif question_type == "comparison":
            tools.append("compare_two_tickers")

            # Add context if question is qualitative
            needs_context = (
                "why" in question_lower
                or "how" in question_lower
                or "recent" in question_lower
                or "news" in question_lower
            )

            if needs_context:
                tools.append("retrieve_context")

        # For risk analysis
        elif question_type == "risk_analysis":
            if tickers:
                tools.append("compute_ratios")
            tools.append("retrieve_context")

        # For general questions
        else:
            tools.append("retrieve_context")
            if tickers:
                tools.append("compute_ratios")

        return tools

    def create_plan(
        self, question: str, ticker: str | None = None
    ) -> dict[str, Any]:
        """
        Create a complete execution plan for answering the question.

        Args:
            question: User question
            ticker: Optional ticker hint

        Returns:
            Dictionary with plan details
        """
        logger.info(f"Creating plan for question: {question[:100]}...")

        # Extract tickers
        tickers = self.extract_tickers(question, ticker)

        # Classify question
        question_type = self.classify_question_type(question, tickers)

        # Determine tools
        tools_needed = self.determine_tools_needed(question, question_type, tickers)

        # Determine prompt type
        if question_type == "comparison":
            prompt_type = "comparison"
        elif question_type == "risk_analysis":
            prompt_type = "risk_analysis"
        elif question_type == "single_ticker":
            prompt_type = "single_ticker"
        else:
            prompt_type = "general"

        plan = {
            "question": question,
            "tickers": tickers,
            "question_type": question_type,
            "tools": tools_needed,
            "prompt_type": prompt_type,
            "needs_financial_data": "compute_ratios" in tools_needed
            or "compare_two_tickers" in tools_needed,
            "needs_context": "retrieve_context" in tools_needed,
        }

        logger.info(f"Plan created: type={question_type}, tools={tools_needed}, tickers={tickers}")

        return plan

    def refine_plan(self, plan: dict[str, Any], tool_results: dict[str, Any]) -> dict[str, Any]:
        """
        Refine the plan based on tool execution results.

        Args:
            plan: Original plan
            tool_results: Results from executed tools

        Returns:
            Updated plan
        """
        # Check if we need additional tools based on results
        additional_tools = []

        # If comparison failed due to missing ticker, add fetch tickers tool
        if plan["question_type"] == "comparison" and len(plan["tickers"]) < 2:
            additional_tools.append("get_available_tickers")

        # If no context retrieved, might need to fetch news directly
        if plan["needs_context"] and "retrieve_context" in tool_results:
            context_result = tool_results["retrieve_context"]
            if context_result.get("num_docs", 0) == 0:
                additional_tools.append("get_ticker_news")

        if additional_tools:
            plan["tools"].extend(additional_tools)
            logger.info(f"Plan refined: added tools {additional_tools}")

        return plan


if __name__ == "__main__":
    # Test planner
    logging.basicConfig(level=logging.INFO)

    print("Testing Agent Planner\n" + "=" * 80)

    planner = AgentPlanner()

    # Test cases
    test_cases = [
        ("What are the key financial metrics for Apple?", "AAPL"),
        ("Compare Apple and Microsoft's profitability", None),
        ("What are the main risks for NVDA?", None),
        ("Which tech companies are growing fastest?", None),
        ("AAPL vs MSFT: which has better margins?", None),
        ("Tell me about recent earnings results for TSLA", "TSLA"),
    ]

    for i, (question, ticker) in enumerate(test_cases, 1):
        print(f"\n{i}. Question: {question}")
        print(f"   Ticker hint: {ticker}")
        print("-" * 80)

        plan = planner.create_plan(question, ticker)

        print(f"   Type: {plan['question_type']}")
        print(f"   Tickers: {plan['tickers']}")
        print(f"   Tools: {plan['tools']}")
        print(f"   Prompt type: {plan['prompt_type']}")
