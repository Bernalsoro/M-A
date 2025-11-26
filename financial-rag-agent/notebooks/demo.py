"""
Financial RAG Agent - Demo Script

Demonstrates key capabilities of the system with practical examples.

Run this script to see the agent in action:
    python notebooks/demo.py
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from financial_rag_agent.agents.agent import FinancialAgent
from financial_rag_agent.ingestion.loader import DataLoader
from financial_rag_agent.retrieval.vector_store import build_vector_store_from_news

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: dict, verbose: bool = True):
    """
    Print agent result in a formatted way.

    Args:
        result: Agent response dictionary
        verbose: Whether to print detailed information
    """
    print(f"Question: {result['question']}")
    if result.get("ticker"):
        print(f"Ticker: {result['ticker']}")

    print(f"\nPlan: {result.get('plan', {}).get('question_type', 'N/A')}")
    print(f"Tools Used: {', '.join(result.get('used_tools', []))}")
    print(f"Execution Time: {result.get('execution_time_ms', 0):.0f}ms")

    print(f"\n{'-' * 80}")
    print("ANSWER:")
    print("-" * 80)
    print(result["final_answer"])

    if verbose and result.get("tool_results"):
        print(f"\n{'-' * 80}")
        print("CONTEXT USED:")
        print("-" * 80)

        # Show retrieved documents
        if "retrieve_context" in result["tool_results"]:
            context_result = result["tool_results"]["retrieve_context"]
            if context_result.get("success"):
                docs = context_result.get("documents", [])
                print(f"\nRetrieved {len(docs)} documents:")
                for i, doc in enumerate(docs[:3], 1):  # Show first 3
                    print(f"\n{i}. {doc.get('headline', 'N/A')}")
                    print(f"   Ticker: {doc.get('ticker')} | Score: {doc.get('score', 0):.3f}")

        # Show financial metrics
        if "compute_ratios" in result["tool_results"]:
            ratios_result = result["tool_results"]["compute_ratios"]
            if ratios_result.get("success"):
                data = ratios_result["data"]
                print(f"\nKey Financial Metrics:")
                print(f"  Revenue: ${data.get('revenue', 0):,.0f}M")
                print(f"  Net Margin: {data.get('net_margin', 0):.1f}%")
                print(f"  ROE: {data.get('roe', 0):.1f}%")
                print(f"  Revenue Growth YoY: {data.get('revenue_growth_yoy', 0):.1f}%")


def initialize_system():
    """Initialize the RAG system (load data, build index)."""
    print_section("INITIALIZING FINANCIAL RAG AGENT")

    print("Step 1: Loading financial data...")
    loader = DataLoader()
    financials = loader.load_financials()
    news = loader.load_news()
    print(f"✓ Loaded {len(financials)} financial records")
    print(f"✓ Loaded {len(news)} news items")

    print("\nStep 2: Building vector store...")
    vector_store = build_vector_store_from_news(news, save=True)
    print(f"✓ Vector store created with {vector_store.size} documents")

    print("\nStep 3: Initializing agent...")
    agent = FinancialAgent()
    status = agent.get_status()
    print(f"✓ Agent initialized")
    print(f"  LLM: {status['llm']['provider']} - {status['llm']['model']}")
    print(f"  LLM Available: {status['llm']['available']}")
    print(f"  Vector Store: {status['vector_store']['num_documents']} documents")

    return agent


def demo_single_ticker_analysis(agent: FinancialAgent):
    """Demo: Analyze a single ticker."""
    print_section("DEMO 1: SINGLE TICKER ANALYSIS")

    question = "What are the key financial highlights from Apple's recent earnings?"
    print(f"Query: {question}\n")

    result = agent.answer(ticker="AAPL", question=question)
    print_result(result, verbose=True)


def demo_comparative_analysis(agent: FinancialAgent):
    """Demo: Compare two tickers."""
    print_section("DEMO 2: COMPARATIVE ANALYSIS")

    question = "Compare Apple and Microsoft's profitability. Which company has better margins?"
    print(f"Query: {question}\n")

    result = agent.answer(question=question)
    print_result(result, verbose=True)


def demo_risk_analysis(agent: FinancialAgent):
    """Demo: Risk assessment for a ticker."""
    print_section("DEMO 3: RISK ANALYSIS")

    question = "What are the main risks facing NVIDIA based on recent developments?"
    print(f"Query: {question}\n")

    result = agent.answer(ticker="NVDA", question=question)
    print_result(result, verbose=True)


def demo_growth_analysis(agent: FinancialAgent):
    """Demo: Growth trajectory analysis."""
    print_section("DEMO 4: GROWTH ANALYSIS")

    question = "Analyze Tesla's growth trajectory and recent performance trends"
    print(f"Query: {question}\n")

    result = agent.answer(ticker="TSLA", question=question)
    print_result(result, verbose=False)  # Less verbose for variety


def demo_sector_comparison(agent: FinancialAgent):
    """Demo: Cross-sector comparison."""
    print_section("DEMO 5: CROSS-COMPANY COMPARISON")

    question = "How do Google and Meta compare in terms of AI investments and revenue growth?"
    print(f"Query: {question}\n")

    result = agent.answer(question=question)
    print_result(result, verbose=False)


def demo_custom_query(agent: FinancialAgent):
    """Demo: Interactive custom query."""
    print_section("DEMO 6: CUSTOM QUERY (INTERACTIVE)")

    print("You can now ask your own question!")
    print("\nExample questions:")
    print("  - What is Amazon's cloud business performance?")
    print("  - Compare NVDA and TSLA growth rates")
    print("  - What are the key risks for META?")

    # In a real interactive demo, you'd use input() here
    # For automated demo, we'll use a preset question
    question = "What is Amazon's cloud business performance and profitability?"
    ticker = "AMZN"

    print(f"\nQuery: {question}")
    print(f"Ticker: {ticker}\n")

    result = agent.answer(ticker=ticker, question=question)
    print_result(result, verbose=False)


def main():
    """Main demo execution."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    FINANCIAL RAG AGENT - DEMO SCRIPT                         ║
║                                                                              ║
║  This demo showcases the Financial RAG Agent's capabilities:                 ║
║    - Single ticker analysis                                                  ║
║    - Comparative analysis                                                    ║
║    - Risk assessment                                                         ║
║    - Growth analysis                                                         ║
║    - Multi-company comparisons                                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Initialize system
        agent = initialize_system()

        # Run demos
        demo_single_ticker_analysis(agent)
        demo_comparative_analysis(agent)
        demo_risk_analysis(agent)
        demo_growth_analysis(agent)
        demo_sector_comparison(agent)
        demo_custom_query(agent)

        # Summary
        print_section("DEMO COMPLETE")
        print("✓ All demonstrations completed successfully")
        print("\nNext steps:")
        print("  1. Start the API: uvicorn financial_rag_agent.api.main:app --reload")
        print("  2. Run tests: pytest tests/ -v")
        print("  3. Run evaluation: python -m financial_rag_agent.evaluation.eval_examples")
        print("\nFor production use:")
        print("  - Configure your OpenAI/Anthropic API keys in .env")
        print("  - Review and adjust settings in src/financial_rag_agent/config.py")
        print("  - Add your own financial data to src/financial_rag_agent/data/")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("  1. Data files exist in src/financial_rag_agent/data/")
        print("  2. All dependencies are installed: pip install -e .")
        print("  3. Python version is 3.10+")
        sys.exit(1)


if __name__ == "__main__":
    main()
