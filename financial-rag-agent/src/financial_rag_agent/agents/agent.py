"""
Main Financial Agent implementation.

Orchestrates the complete RAG + Agent workflow:
1. Planning: Analyze question and determine strategy
2. Tool Execution: Fetch data, compute ratios, retrieve context
3. Synthesis: Generate answer using LLM with retrieved information
"""

import logging
import time
from typing import Any

from financial_rag_agent.agents.planner import AgentPlanner
from financial_rag_agent.agents.tools import FinancialTools
from financial_rag_agent.config import settings
from financial_rag_agent.llm.llm_client import LLMClient
from financial_rag_agent.llm.prompts import PromptBuilder

logger = logging.getLogger(__name__)


class FinancialAgent:
    """Main agent for financial analysis."""

    def __init__(
        self,
        tools: FinancialTools | None = None,
        planner: AgentPlanner | None = None,
        llm_client: LLMClient | None = None,
        enable_planning: bool | None = None,
    ):
        """
        Initialize the Financial Agent.

        Args:
            tools: Financial tools instance
            planner: Agent planner instance
            llm_client: LLM client instance
            enable_planning: Whether to use planning (default from settings)
        """
        self.tools = tools or FinancialTools()
        self.planner = planner or AgentPlanner()
        self.llm_client = llm_client or LLMClient()
        self.enable_planning = (
            enable_planning if enable_planning is not None else settings.agent_enable_planning
        )

        logger.info("Financial Agent initialized")
        logger.info(f"  LLM: {self.llm_client.provider} - {self.llm_client.model}")
        logger.info(f"  Planning: {'enabled' if self.enable_planning else 'disabled'}")

    def answer(
        self, ticker: str | None = None, question: str | None = None, **kwargs
    ) -> dict[str, Any]:
        """
        Main interface: Answer a financial question.

        Args:
            ticker: Optional ticker symbol
            question: Financial question
            **kwargs: Additional parameters (top_k, temperature, etc.)

        Returns:
            Dictionary with answer and metadata
        """
        if not question:
            raise ValueError("Question is required")

        start_time = time.time()

        logger.info(f"Agent answering: {question[:100]}...")
        if ticker:
            logger.info(f"  Ticker: {ticker}")

        try:
            # Step 1: Planning
            if self.enable_planning:
                plan = self.planner.create_plan(question, ticker)
                logger.info(f"  Plan: {plan['question_type']} | Tools: {plan['tools']}")
            else:
                # Simple fallback if planning disabled
                plan = {
                    "question": question,
                    "tickers": [ticker] if ticker else [],
                    "question_type": "general",
                    "tools": ["compute_ratios", "retrieve_context"],
                    "prompt_type": "general",
                }

            # Step 2: Tool Execution
            tool_results = self._execute_tools(plan)

            # Step 3: Synthesize Answer
            answer = self._synthesize_answer(plan, tool_results)

            # Compile results
            execution_time = (time.time() - start_time) * 1000  # ms

            result = {
                "final_answer": answer,
                "question": question,
                "ticker": ticker,
                "plan": plan,
                "used_tools": list(tool_results.keys()),
                "tool_results": tool_results,
                "execution_time_ms": round(execution_time, 2),
                "llm_available": self.llm_client.is_available(),
            }

            logger.info(f"  Completed in {execution_time:.0f}ms")
            return result

        except Exception as e:
            logger.error(f"Error in agent execution: {e}", exc_info=True)
            return {
                "final_answer": f"Error processing question: {str(e)}",
                "question": question,
                "ticker": ticker,
                "error": str(e),
                "success": False,
            }

    def _execute_tools(self, plan: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the tools specified in the plan.

        Args:
            plan: Execution plan from planner

        Returns:
            Dictionary mapping tool names to their results
        """
        results = {}
        tickers = plan["tickers"]
        question = plan["question"]

        for tool_name in plan["tools"]:
            logger.info(f"  Executing tool: {tool_name}")

            try:
                if tool_name == "fetch_financials":
                    if tickers:
                        results[tool_name] = self.tools.fetch_financials(tickers[0])

                elif tool_name == "compute_ratios":
                    if tickers:
                        results[tool_name] = self.tools.compute_ratios(tickers[0])

                elif tool_name == "retrieve_context":
                    if tickers:
                        results[tool_name] = self.tools.retrieve_context(tickers[0], question)
                    else:
                        # General retrieval without ticker filter
                        context_result = self.tools.retriever.retrieve_general(question)
                        formatted = self.tools.retriever.format_context_for_llm(context_result)
                        results[tool_name] = {
                            "tool": "retrieve_context",
                            "success": True,
                            "documents": context_result,
                            "formatted_context": formatted,
                            "num_docs": len(context_result),
                        }

                elif tool_name == "compare_two_tickers":
                    if len(tickers) >= 2:
                        results[tool_name] = self.tools.compare_two_tickers(
                            tickers[0], tickers[1], question
                        )
                    else:
                        logger.warning(f"Not enough tickers for comparison: {tickers}")

                elif tool_name == "get_available_tickers":
                    results[tool_name] = self.tools.get_available_tickers()

                elif tool_name == "get_ticker_news":
                    if tickers:
                        results[tool_name] = self.tools.get_ticker_news(tickers[0])

                else:
                    logger.warning(f"Unknown tool: {tool_name}")

            except Exception as e:
                logger.error(f"Error executing {tool_name}: {e}")
                results[tool_name] = {
                    "tool": tool_name,
                    "success": False,
                    "error": str(e),
                }

        return results

    def _synthesize_answer(self, plan: dict[str, Any], tool_results: dict[str, Any]) -> str:
        """
        Synthesize final answer using LLM.

        Args:
            plan: Execution plan
            tool_results: Results from tool execution

        Returns:
            Generated answer
        """
        logger.info("  Synthesizing answer with LLM...")

        # Extract data from tool results
        financial_data = None
        context = ""
        tickers = plan["tickers"]
        question = plan["question"]

        # Get financial data
        if "compute_ratios" in tool_results:
            ratios_result = tool_results["compute_ratios"]
            if ratios_result.get("success"):
                financial_data = ratios_result["data"]

        # Get context
        if "retrieve_context" in tool_results:
            context_result = tool_results["retrieve_context"]
            if context_result.get("success"):
                context = context_result.get("formatted_context", "")

        # Build appropriate prompt based on plan
        prompt_type = plan.get("prompt_type", "general")

        if prompt_type == "comparison" and len(tickers) >= 2:
            # Comparison prompt
            compare_result = tool_results.get("compare_two_tickers", {})
            if compare_result.get("success"):
                financial_data1 = compare_result.get("summary1", {})
                financial_data2 = compare_result.get("summary2", {})

                # Get context for both tickers
                context_data = compare_result.get("context", {})
                if context_data:
                    context1 = self.tools.retriever.format_context_for_llm(
                        context_data.get(tickers[0], [])
                    )
                    context2 = self.tools.retriever.format_context_for_llm(
                        context_data.get(tickers[1], [])
                    )
                else:
                    context1 = context
                    context2 = context

                system_prompt, user_prompt = PromptBuilder.build_comparison_prompt(
                    tickers[0],
                    tickers[1],
                    question,
                    financial_data1,
                    financial_data2,
                    context1,
                    context2,
                )
            else:
                # Fallback to general if comparison failed
                system_prompt, user_prompt = PromptBuilder.build_general_prompt(
                    question, context, financial_data
                )

        elif prompt_type == "risk_analysis" and tickers:
            # Risk analysis prompt
            system_prompt, user_prompt = PromptBuilder.build_risk_analysis_prompt(
                tickers[0], financial_data or {}, context
            )

        elif prompt_type == "single_ticker" and tickers:
            # Single ticker analysis
            system_prompt, user_prompt = PromptBuilder.build_single_ticker_analysis_prompt(
                tickers[0], question, financial_data or {}, context
            )

        else:
            # General prompt
            system_prompt, user_prompt = PromptBuilder.build_general_prompt(
                question, context, financial_data
            )

        # Generate answer
        answer = self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        return answer

    def get_status(self) -> dict[str, Any]:
        """
        Get agent status and configuration.

        Returns:
            Dictionary with status information
        """
        return {
            "agent": "FinancialAgent",
            "version": "0.1.0",
            "llm": self.llm_client.get_model_info(),
            "vector_store": self.tools.retriever.get_vector_store_info(),
            "planning_enabled": self.enable_planning,
            "available_tools": list(self.tools.get_tool_descriptions().keys()),
        }


if __name__ == "__main__":
    # Test agent
    logging.basicConfig(level=logging.INFO)

    print("Testing Financial Agent\n" + "=" * 80)

    agent = FinancialAgent()

    # Print status
    print("\nAgent Status:")
    print("-" * 80)
    status = agent.get_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    # Test queries
    test_queries = [
        ("AAPL", "What are the key financial highlights from recent earnings?"),
        ("NVDA", "What are the main risks facing the company?"),
        (None, "Compare AAPL and MSFT profitability"),
    ]

    for i, (ticker, question) in enumerate(test_queries, 1):
        print(f"\n\nTest {i}: {question}")
        print(f"Ticker: {ticker}")
        print("=" * 80)

        result = agent.answer(ticker=ticker, question=question)

        print(f"\nPlan: {result.get('plan', {}).get('question_type')}")
        print(f"Tools used: {result.get('used_tools', [])}")
        print(f"Execution time: {result.get('execution_time_ms', 0):.0f}ms")
        print(f"\nAnswer:\n{result['final_answer'][:500]}...")
