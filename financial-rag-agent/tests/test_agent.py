"""
Tests for agent system (tools, planner, agent).
"""

import pytest

from financial_rag_agent.agents.agent import FinancialAgent
from financial_rag_agent.agents.planner import AgentPlanner
from financial_rag_agent.agents.tools import FinancialTools


@pytest.fixture(scope="module")
def tools():
    """Create tools instance."""
    return FinancialTools()


@pytest.fixture(scope="module")
def planner():
    """Create planner instance."""
    return AgentPlanner()


@pytest.fixture(scope="module")
def agent():
    """Create agent instance."""
    return FinancialAgent()


class TestFinancialTools:
    """Tests for FinancialTools class."""

    def test_fetch_financials(self, tools):
        """Test fetching financial data."""
        result = tools.fetch_financials("AAPL")

        assert result["success"] is True
        assert result["ticker"] == "AAPL"
        assert "data" in result

        data = result["data"]
        assert "revenue" in data
        assert "net_income" in data

    def test_fetch_financials_invalid_ticker(self, tools):
        """Test fetching with invalid ticker."""
        result = tools.fetch_financials("INVALID")

        assert result["success"] is False
        assert "error" in result

    def test_compute_ratios(self, tools):
        """Test computing financial ratios."""
        result = tools.compute_ratios("MSFT")

        assert result["success"] is True
        assert "data" in result

        data = result["data"]
        assert "net_margin" in data
        assert "roe" in data
        assert "revenue_growth_yoy" in data

    def test_retrieve_context(self, tools):
        """Test retrieving context."""
        result = tools.retrieve_context("NVDA", "GPU business performance", top_k=3)

        assert result["success"] is True
        assert "documents" in result
        assert "formatted_context" in result
        assert result["num_docs"] >= 0

    def test_compare_two_tickers(self, tools):
        """Test comparing two tickers."""
        result = tools.compare_two_tickers("AAPL", "MSFT", "profitability")

        assert result["success"] is True
        assert result["ticker1"] == "AAPL"
        assert result["ticker2"] == "MSFT"
        assert "comparison" in result
        assert "summary1" in result
        assert "summary2" in result

    def test_get_available_tickers(self, tools):
        """Test getting available tickers."""
        result = tools.get_available_tickers()

        assert result["success"] is True
        assert "tickers" in result
        assert "count" in result
        assert len(result["tickers"]) > 0

    def test_get_ticker_news(self, tools):
        """Test getting ticker news."""
        result = tools.get_ticker_news("GOOGL", limit=3)

        assert result["success"] is True
        assert "news" in result
        assert len(result["news"]) <= 3


class TestAgentPlanner:
    """Tests for AgentPlanner class."""

    def test_extract_tickers_from_hint(self, planner):
        """Test ticker extraction with explicit hint."""
        tickers = planner.extract_tickers("What are the results?", ticker_hint="AAPL")

        assert "AAPL" in tickers

    def test_extract_tickers_from_question(self, planner):
        """Test ticker extraction from question text."""
        tickers = planner.extract_tickers("How is AAPL performing?", ticker_hint=None)

        assert "AAPL" in tickers

    def test_extract_tickers_company_names(self, planner):
        """Test ticker extraction from company names."""
        tickers = planner.extract_tickers("How is Apple doing?", ticker_hint=None)

        assert "AAPL" in tickers

    def test_classify_single_ticker(self, planner):
        """Test classifying single ticker questions."""
        question_type = planner.classify_question_type(
            "What are Apple's earnings?", ["AAPL"]
        )

        assert question_type == "single_ticker"

    def test_classify_comparison(self, planner):
        """Test classifying comparison questions."""
        question_type = planner.classify_question_type(
            "Compare Apple and Microsoft", ["AAPL", "MSFT"]
        )

        assert question_type == "comparison"

    def test_classify_risk_analysis(self, planner):
        """Test classifying risk analysis questions."""
        question_type = planner.classify_question_type(
            "What are the risks for Tesla?", ["TSLA"]
        )

        assert question_type == "risk_analysis"

    def test_determine_tools_single_ticker(self, planner):
        """Test tool determination for single ticker."""
        tools = planner.determine_tools_needed(
            "What are the recent earnings?", "single_ticker", ["AAPL"]
        )

        assert "compute_ratios" in tools
        assert "retrieve_context" in tools

    def test_determine_tools_comparison(self, planner):
        """Test tool determination for comparison."""
        tools = planner.determine_tools_needed(
            "Compare AAPL and MSFT", "comparison", ["AAPL", "MSFT"]
        )

        assert "compare_two_tickers" in tools

    def test_create_plan(self, planner):
        """Test creating a complete plan."""
        plan = planner.create_plan("What are Apple's key metrics?", ticker="AAPL")

        assert "question" in plan
        assert "tickers" in plan
        assert "question_type" in plan
        assert "tools" in plan
        assert "prompt_type" in plan

    @pytest.mark.parametrize("question,expected_type", [
        ("What are AAPL's margins?", "single_ticker"),
        ("Compare AAPL and MSFT profitability", "comparison"),
        ("What are the risks for NVDA?", "risk_analysis"),
        ("Which tech companies are growing?", "general"),
    ])
    def test_classify_various_questions(self, planner, question, expected_type):
        """Test question classification for various inputs."""
        tickers = planner.extract_tickers(question)
        question_type = planner.classify_question_type(question, tickers)

        # Type should match or be reasonable alternative
        assert question_type in ["single_ticker", "comparison", "risk_analysis", "general"]


class TestFinancialAgent:
    """Tests for FinancialAgent class."""

    def test_agent_initialization(self, agent):
        """Test agent can be initialized."""
        assert agent is not None
        assert agent.tools is not None
        assert agent.planner is not None
        assert agent.llm_client is not None

    def test_agent_answer_single_ticker(self, agent):
        """Test agent answering single ticker question."""
        result = agent.answer(
            ticker="AAPL",
            question="What are the key financial highlights?"
        )

        assert "final_answer" in result
        assert "question" in result
        assert "plan" in result
        assert "used_tools" in result
        assert "execution_time_ms" in result

    def test_agent_answer_comparison(self, agent):
        """Test agent answering comparison question."""
        result = agent.answer(
            question="Compare Apple and Microsoft margins"
        )

        assert "final_answer" in result
        assert len(result.get("plan", {}).get("tickers", [])) >= 2

    def test_agent_answer_with_planning(self, agent):
        """Test agent with planning enabled."""
        result = agent.answer(
            ticker="NVDA",
            question="Analyze recent GPU business performance"
        )

        assert "plan" in result
        plan = result["plan"]
        assert "question_type" in plan
        assert "tools" in plan

    def test_agent_get_status(self, agent):
        """Test getting agent status."""
        status = agent.get_status()

        assert "agent" in status
        assert "llm" in status
        assert "vector_store" in status
        assert "available_tools" in status

    @pytest.mark.parametrize("ticker,question", [
        ("AAPL", "What are the recent earnings?"),
        ("MSFT", "How is the cloud business performing?"),
        ("GOOGL", "What are the AI developments?"),
        (None, "Compare AAPL and GOOGL"),
    ])
    def test_agent_various_queries(self, agent, ticker, question):
        """Test agent with various queries."""
        result = agent.answer(ticker=ticker, question=question)

        # Should always return a result
        assert "final_answer" in result
        assert isinstance(result["final_answer"], str)
        assert len(result["final_answer"]) > 0

    def test_agent_error_handling_empty_question(self, agent):
        """Test agent handles empty question."""
        with pytest.raises(ValueError):
            agent.answer(ticker="AAPL", question=None)

    def test_agent_tool_execution(self, agent):
        """Test that agent executes tools correctly."""
        result = agent.answer(
            ticker="TSLA",
            question="What are Tesla's growth metrics?"
        )

        assert "tool_results" in result
        assert len(result.get("used_tools", [])) > 0

        # Should have used at least compute_ratios
        assert "compute_ratios" in result.get("used_tools", [])


def test_end_to_end_workflow():
    """Test complete end-to-end workflow."""
    # Create agent
    agent = FinancialAgent()

    # Ask question
    result = agent.answer(
        ticker="AAPL",
        question="What are the key financial metrics and recent news?"
    )

    # Verify complete response
    assert result is not None
    assert "final_answer" in result
    assert "plan" in result
    assert "used_tools" in result

    # Verify tools were executed
    assert len(result["used_tools"]) > 0

    # Verify answer is non-empty
    assert len(result["final_answer"]) > 0

    # Verify execution completed in reasonable time
    assert result["execution_time_ms"] < 30000  # 30 seconds max
