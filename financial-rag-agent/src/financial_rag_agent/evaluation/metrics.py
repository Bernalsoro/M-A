"""
Evaluation metrics for RAG system.

Includes metrics for:
- Retrieval quality (relevance, coverage)
- Answer quality (factuality, completeness)
- System performance (latency, tool usage)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RetrievalMetrics:
    """Metrics for evaluating retrieval quality."""

    @staticmethod
    def precision_at_k(retrieved_docs: list[dict], relevant_tickers: list[str], k: int = 5) -> float:
        """
        Calculate precision@k for retrieval.

        Args:
            retrieved_docs: List of retrieved documents
            relevant_tickers: List of relevant ticker symbols
            k: Number of top documents to consider

        Returns:
            Precision@k score (0-1)
        """
        if not retrieved_docs or not relevant_tickers:
            return 0.0

        top_k = retrieved_docs[:k]
        relevant_count = sum(
            1 for doc in top_k if doc.get("ticker") in relevant_tickers
        )

        return relevant_count / min(k, len(top_k))

    @staticmethod
    def recall_at_k(retrieved_docs: list[dict], relevant_tickers: list[str], k: int = 5) -> float:
        """
        Calculate recall@k for retrieval.

        Args:
            retrieved_docs: List of retrieved documents
            relevant_tickers: List of relevant ticker symbols
            k: Number of top documents to consider

        Returns:
            Recall@k score (0-1)
        """
        if not retrieved_docs or not relevant_tickers:
            return 0.0

        top_k = retrieved_docs[:k]
        retrieved_tickers = set(doc.get("ticker") for doc in top_k)
        relevant_count = sum(1 for ticker in relevant_tickers if ticker in retrieved_tickers)

        return relevant_count / len(relevant_tickers)

    @staticmethod
    def mean_reciprocal_rank(retrieved_docs: list[dict], relevant_tickers: list[str]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR).

        Args:
            retrieved_docs: List of retrieved documents
            relevant_tickers: List of relevant ticker symbols

        Returns:
            MRR score (0-1)
        """
        if not retrieved_docs or not relevant_tickers:
            return 0.0

        for i, doc in enumerate(retrieved_docs, 1):
            if doc.get("ticker") in relevant_tickers:
                return 1.0 / i

        return 0.0

    @staticmethod
    def average_score(retrieved_docs: list[dict], k: int = 5) -> float:
        """
        Calculate average relevance score of top-k retrieved documents.

        Args:
            retrieved_docs: List of retrieved documents with scores
            k: Number of top documents to consider

        Returns:
            Average score (0-1)
        """
        if not retrieved_docs:
            return 0.0

        top_k = retrieved_docs[:k]
        scores = [doc.get("score", 0.0) for doc in top_k]

        return sum(scores) / len(scores) if scores else 0.0


class AnswerMetrics:
    """Metrics for evaluating answer quality."""

    @staticmethod
    def contains_key_facts(answer: str, key_facts: list[str]) -> dict[str, Any]:
        """
        Check if answer contains expected key facts.

        Args:
            answer: Generated answer
            key_facts: List of expected facts (as substrings)

        Returns:
            Dictionary with coverage metrics
        """
        answer_lower = answer.lower()

        found_facts = []
        missing_facts = []

        for fact in key_facts:
            if fact.lower() in answer_lower:
                found_facts.append(fact)
            else:
                missing_facts.append(fact)

        coverage = len(found_facts) / len(key_facts) if key_facts else 0.0

        return {
            "coverage": coverage,
            "found_facts": found_facts,
            "missing_facts": missing_facts,
            "total_facts": len(key_facts),
        }

    @staticmethod
    def check_ticker_mention(answer: str, expected_tickers: list[str]) -> dict[str, Any]:
        """
        Check if expected tickers are mentioned in the answer.

        Args:
            answer: Generated answer
            expected_tickers: List of ticker symbols that should appear

        Returns:
            Dictionary with ticker mention metrics
        """
        mentioned = []
        not_mentioned = []

        for ticker in expected_tickers:
            if ticker in answer.upper():
                mentioned.append(ticker)
            else:
                not_mentioned.append(ticker)

        return {
            "mentioned": mentioned,
            "not_mentioned": not_mentioned,
            "mention_rate": len(mentioned) / len(expected_tickers) if expected_tickers else 0.0,
        }

    @staticmethod
    def answer_length_analysis(answer: str) -> dict[str, Any]:
        """
        Analyze answer length and structure.

        Args:
            answer: Generated answer

        Returns:
            Dictionary with length metrics
        """
        words = answer.split()
        sentences = answer.split(".")

        return {
            "char_count": len(answer),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0,
        }


class SystemMetrics:
    """Metrics for evaluating system performance."""

    @staticmethod
    def tool_usage_efficiency(
        used_tools: list[str], optimal_tools: list[str]
    ) -> dict[str, Any]:
        """
        Evaluate tool usage efficiency.

        Args:
            used_tools: List of tools actually used
            optimal_tools: List of optimal tools for the task

        Returns:
            Dictionary with efficiency metrics
        """
        used_set = set(used_tools)
        optimal_set = set(optimal_tools)

        necessary_tools = used_set.intersection(optimal_set)
        unnecessary_tools = used_set - optimal_set
        missing_tools = optimal_set - used_set

        precision = len(necessary_tools) / len(used_set) if used_set else 0.0
        recall = len(necessary_tools) / len(optimal_set) if optimal_set else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "necessary_tools": list(necessary_tools),
            "unnecessary_tools": list(unnecessary_tools),
            "missing_tools": list(missing_tools),
            "total_used": len(used_tools),
            "total_optimal": len(optimal_tools),
        }

    @staticmethod
    def latency_analysis(execution_time_ms: float) -> dict[str, Any]:
        """
        Analyze system latency.

        Args:
            execution_time_ms: Execution time in milliseconds

        Returns:
            Dictionary with latency assessment
        """
        # Define thresholds
        excellent_threshold = 1000  # 1s
        good_threshold = 3000  # 3s
        acceptable_threshold = 5000  # 5s

        if execution_time_ms < excellent_threshold:
            category = "excellent"
        elif execution_time_ms < good_threshold:
            category = "good"
        elif execution_time_ms < acceptable_threshold:
            category = "acceptable"
        else:
            category = "slow"

        return {
            "execution_time_ms": execution_time_ms,
            "execution_time_s": execution_time_ms / 1000,
            "category": category,
            "meets_sla": execution_time_ms < acceptable_threshold,
        }


def evaluate_agent_response(
    response: dict[str, Any],
    expected_tickers: list[str] | None = None,
    key_facts: list[str] | None = None,
    optimal_tools: list[str] | None = None,
) -> dict[str, Any]:
    """
    Comprehensive evaluation of an agent response.

    Args:
        response: Agent response dictionary
        expected_tickers: Expected ticker symbols
        key_facts: Expected key facts in answer
        optimal_tools: Optimal tool set for the question

    Returns:
        Dictionary with comprehensive evaluation metrics
    """
    evaluation = {
        "question": response.get("question"),
        "execution_successful": response.get("success", True),
    }

    # Retrieval metrics
    if "tool_results" in response and "retrieve_context" in response["tool_results"]:
        context_result = response["tool_results"]["retrieve_context"]
        if context_result.get("success") and expected_tickers:
            retrieved_docs = context_result.get("documents", [])
            evaluation["retrieval"] = {
                "precision_at_5": RetrievalMetrics.precision_at_k(
                    retrieved_docs, expected_tickers, 5
                ),
                "recall_at_5": RetrievalMetrics.recall_at_k(retrieved_docs, expected_tickers, 5),
                "mrr": RetrievalMetrics.mean_reciprocal_rank(retrieved_docs, expected_tickers),
                "avg_score": RetrievalMetrics.average_score(retrieved_docs, 5),
            }

    # Answer quality metrics
    answer = response.get("final_answer", "")
    if answer:
        evaluation["answer_length"] = AnswerMetrics.answer_length_analysis(answer)

        if expected_tickers:
            evaluation["ticker_mentions"] = AnswerMetrics.check_ticker_mention(
                answer, expected_tickers
            )

        if key_facts:
            evaluation["fact_coverage"] = AnswerMetrics.contains_key_facts(answer, key_facts)

    # System performance metrics
    if "execution_time_ms" in response:
        evaluation["latency"] = SystemMetrics.latency_analysis(response["execution_time_ms"])

    if "used_tools" in response and optimal_tools:
        evaluation["tool_efficiency"] = SystemMetrics.tool_usage_efficiency(
            response["used_tools"], optimal_tools
        )

    return evaluation


if __name__ == "__main__":
    # Test metrics
    print("Testing Evaluation Metrics\n" + "=" * 80)

    # Test retrieval metrics
    retrieved_docs = [
        {"ticker": "AAPL", "score": 0.92},
        {"ticker": "MSFT", "score": 0.85},
        {"ticker": "GOOGL", "score": 0.78},
        {"ticker": "NVDA", "score": 0.71},
        {"ticker": "AMZN", "score": 0.65},
    ]
    relevant_tickers = ["AAPL", "MSFT"]

    print("\n1. Retrieval Metrics")
    print("-" * 80)
    print(f"Precision@5: {RetrievalMetrics.precision_at_k(retrieved_docs, relevant_tickers, 5):.2f}")
    print(f"Recall@5: {RetrievalMetrics.recall_at_k(retrieved_docs, relevant_tickers, 5):.2f}")
    print(f"MRR: {RetrievalMetrics.mean_reciprocal_rank(retrieved_docs, relevant_tickers):.2f}")
    print(f"Avg Score: {RetrievalMetrics.average_score(retrieved_docs, 5):.2f}")

    # Test answer metrics
    answer = "AAPL reported strong revenue growth of 6% YoY with improved margins."
    key_facts = ["revenue growth", "margins", "6%"]

    print("\n2. Answer Quality Metrics")
    print("-" * 80)
    fact_coverage = AnswerMetrics.contains_key_facts(answer, key_facts)
    print(f"Fact Coverage: {fact_coverage['coverage']:.2f}")
    print(f"Found Facts: {fact_coverage['found_facts']}")

    ticker_check = AnswerMetrics.check_ticker_mention(answer, ["AAPL", "MSFT"])
    print(f"Ticker Mention Rate: {ticker_check['mention_rate']:.2f}")
    print(f"Mentioned: {ticker_check['mentioned']}")

    # Test system metrics
    print("\n3. System Performance Metrics")
    print("-" * 80)
    tool_efficiency = SystemMetrics.tool_usage_efficiency(
        ["compute_ratios", "retrieve_context"], ["compute_ratios", "retrieve_context"]
    )
    print(f"Tool Precision: {tool_efficiency['precision']:.2f}")
    print(f"Tool Recall: {tool_efficiency['recall']:.2f}")

    latency = SystemMetrics.latency_analysis(1450)
    print(f"Latency: {latency['execution_time_ms']}ms ({latency['category']})")
