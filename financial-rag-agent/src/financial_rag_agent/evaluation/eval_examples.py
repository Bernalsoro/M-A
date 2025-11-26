"""
Evaluation examples and test cases for the Financial RAG Agent.

Provides curated test cases with expected outcomes for benchmarking.
"""

import logging
from typing import Any

from financial_rag_agent.agents.agent import FinancialAgent
from financial_rag_agent.evaluation.metrics import evaluate_agent_response

logger = logging.getLogger(__name__)


class EvaluationSuite:
    """Suite of evaluation test cases."""

    # Test cases with expected outcomes
    TEST_CASES = [
        {
            "id": "single_ticker_earnings",
            "ticker": "AAPL",
            "question": "What are the key highlights from Apple's recent earnings?",
            "expected_tickers": ["AAPL"],
            "expected_tools": ["compute_ratios", "retrieve_context"],
            "key_facts": ["revenue", "growth", "margin"],
            "question_type": "single_ticker",
        },
        {
            "id": "comparison_profitability",
            "ticker": None,
            "question": "Compare Apple and Microsoft's profitability metrics",
            "expected_tickers": ["AAPL", "MSFT"],
            "expected_tools": ["compare_two_tickers"],
            "key_facts": ["margin", "roe", "profitability"],
            "question_type": "comparison",
        },
        {
            "id": "risk_analysis",
            "ticker": "NVDA",
            "question": "What are the main risks facing NVIDIA?",
            "expected_tickers": ["NVDA"],
            "expected_tools": ["compute_ratios", "retrieve_context"],
            "key_facts": ["risk", "challenge"],
            "question_type": "risk_analysis",
        },
        {
            "id": "growth_analysis",
            "ticker": "TSLA",
            "question": "Analyze Tesla's growth trajectory and outlook",
            "expected_tickers": ["TSLA"],
            "expected_tools": ["compute_ratios", "retrieve_context"],
            "key_facts": ["growth", "revenue", "outlook"],
            "question_type": "single_ticker",
        },
        {
            "id": "comparison_tech_leaders",
            "ticker": None,
            "question": "Compare GOOGL and META: which has better margins?",
            "expected_tickers": ["GOOGL", "META"],
            "expected_tools": ["compare_two_tickers"],
            "key_facts": ["margin", "profitability"],
            "question_type": "comparison",
        },
        {
            "id": "cloud_business",
            "ticker": "AMZN",
            "question": "How is Amazon's cloud business performing?",
            "expected_tickers": ["AMZN"],
            "expected_tools": ["compute_ratios", "retrieve_context"],
            "key_facts": ["aws", "cloud", "growth"],
            "question_type": "single_ticker",
        },
    ]

    def __init__(self, agent: FinancialAgent | None = None):
        """
        Initialize evaluation suite.

        Args:
            agent: FinancialAgent instance (creates new if not provided)
        """
        self.agent = agent or FinancialAgent()
        self.results = []

    def run_test_case(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """
        Run a single test case.

        Args:
            test_case: Test case dictionary

        Returns:
            Dictionary with test results and evaluation
        """
        logger.info(f"Running test case: {test_case['id']}")

        # Execute agent
        response = self.agent.answer(
            ticker=test_case["ticker"],
            question=test_case["question"],
        )

        # Evaluate response
        evaluation = evaluate_agent_response(
            response,
            expected_tickers=test_case.get("expected_tickers"),
            key_facts=test_case.get("key_facts"),
            optimal_tools=test_case.get("expected_tools"),
        )

        result = {
            "test_case_id": test_case["id"],
            "test_case": test_case,
            "response": response,
            "evaluation": evaluation,
        }

        return result

    def run_all_tests(self) -> list[dict[str, Any]]:
        """
        Run all test cases in the suite.

        Returns:
            List of test results
        """
        logger.info(f"Running {len(self.TEST_CASES)} test cases")

        results = []
        for test_case in self.TEST_CASES:
            try:
                result = self.run_test_case(test_case)
                results.append(result)
            except Exception as e:
                logger.error(f"Test case {test_case['id']} failed: {e}")
                results.append({
                    "test_case_id": test_case["id"],
                    "test_case": test_case,
                    "error": str(e),
                    "success": False,
                })

        self.results = results
        logger.info(f"Completed {len(results)} test cases")
        return results

    def print_summary(self):
        """Print summary of evaluation results."""
        if not self.results:
            print("No results to summarize. Run tests first.")
            return

        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)

        successful = sum(1 for r in self.results if r.get("response", {}).get("success", True))
        failed = len(self.results) - successful

        print(f"\nTotal Test Cases: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

        # Aggregate metrics
        avg_latency = []
        avg_tool_precision = []
        avg_tool_recall = []

        for result in self.results:
            eval_data = result.get("evaluation", {})

            if "latency" in eval_data:
                avg_latency.append(eval_data["latency"]["execution_time_ms"])

            if "tool_efficiency" in eval_data:
                avg_tool_precision.append(eval_data["tool_efficiency"]["precision"])
                avg_tool_recall.append(eval_data["tool_efficiency"]["recall"])

        if avg_latency:
            print(f"\nAverage Latency: {sum(avg_latency) / len(avg_latency):.0f}ms")

        if avg_tool_precision:
            print(f"Average Tool Precision: {sum(avg_tool_precision) / len(avg_tool_precision):.2f}")
            print(f"Average Tool Recall: {sum(avg_tool_recall) / len(avg_tool_recall):.2f}")

        # Per test case summary
        print("\n" + "-" * 80)
        print("PER TEST CASE RESULTS")
        print("-" * 80)

        for result in self.results:
            test_id = result["test_case_id"]
            success = result.get("response", {}).get("success", True)
            status = "✓ PASS" if success else "✗ FAIL"

            print(f"\n{status} | {test_id}")

            if not success:
                print(f"  Error: {result.get('error', 'Unknown')}")
                continue

            eval_data = result.get("evaluation", {})

            # Tool efficiency
            if "tool_efficiency" in eval_data:
                tool_eff = eval_data["tool_efficiency"]
                print(f"  Tools: P={tool_eff['precision']:.2f}, R={tool_eff['recall']:.2f}")
                if tool_eff.get("unnecessary_tools"):
                    print(f"  Unnecessary: {tool_eff['unnecessary_tools']}")
                if tool_eff.get("missing_tools"):
                    print(f"  Missing: {tool_eff['missing_tools']}")

            # Latency
            if "latency" in eval_data:
                latency = eval_data["latency"]
                print(f"  Latency: {latency['execution_time_ms']:.0f}ms ({latency['category']})")

            # Fact coverage
            if "fact_coverage" in eval_data:
                coverage = eval_data["fact_coverage"]
                print(f"  Fact Coverage: {coverage['coverage']:.0%}")

            # Answer length
            if "answer_length" in eval_data:
                length = eval_data["answer_length"]
                print(f"  Answer Length: {length['word_count']} words")

    def export_results(self, filepath: str):
        """
        Export results to JSON file.

        Args:
            filepath: Path to export file
        """
        import json

        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results exported to {filepath}")


if __name__ == "__main__":
    # Run evaluation suite
    logging.basicConfig(level=logging.INFO)

    print("Running Financial RAG Agent Evaluation Suite\n" + "=" * 80)

    suite = EvaluationSuite()

    print("\nRunning all test cases...")
    results = suite.run_all_tests()

    print("\nGenerating summary...")
    suite.print_summary()

    # Export results
    # suite.export_results("evaluation_results.json")
