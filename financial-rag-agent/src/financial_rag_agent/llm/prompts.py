"""
Prompt templates for financial analysis.

Contains structured prompts for different types of financial questions and analyses.
"""

from typing import Any


class PromptBuilder:
    """Builder for financial analysis prompts."""

    # System prompts for different personas
    SYSTEM_PROMPTS = {
        "equity_analyst": """You are a senior equity research analyst with deep expertise in financial analysis and valuation.

Your responsibilities:
- Analyze financial statements with focus on profitability, growth, and risk
- Compute and interpret key financial ratios
- Provide objective, data-driven insights
- Highlight both opportunities and risks
- Use precise financial terminology

Your tone should be professional, analytical, and balanced. Avoid making explicit buy/sell recommendations.
Instead, focus on fundamental analysis and let the data speak for itself.""",
        "comparative_analyst": """You are a senior equity research analyst specializing in comparative company analysis.

Your responsibilities:
- Compare multiple companies across key financial metrics
- Identify relative strengths and weaknesses
- Contextualize differences (business model, sector dynamics, maturity)
- Provide balanced perspective on competitive positioning

Focus on objective metrics and avoid subjective preferences. Present both quantitative and qualitative factors.""",
        "risk_analyst": """You are a risk analyst specializing in corporate and financial risk assessment.

Your responsibilities:
- Identify key risk factors from financial data and news
- Assess magnitude and likelihood of risks
- Consider both financial risks (leverage, liquidity) and business risks (competition, regulation)
- Provide actionable risk insights

Be thorough but concise. Focus on material risks that could impact financial performance.""",
    }

    @staticmethod
    def build_single_ticker_analysis_prompt(
        ticker: str,
        question: str,
        financial_data: dict[str, Any],
        context: str,
    ) -> tuple[str, str]:
        """
        Build prompt for single ticker analysis.

        Args:
            ticker: Stock ticker
            question: User question
            financial_data: Dictionary of financial metrics
            context: Retrieved textual context

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = PromptBuilder.SYSTEM_PROMPTS["equity_analyst"]

        # Format financial data
        financial_summary = PromptBuilder._format_financial_data(financial_data)

        user_prompt = f"""
Analyze {ticker} based on the question below. Use the provided financial data and recent news context.

**Question**: {question}

**Financial Data**:
{financial_summary}

**Recent News & Context**:
{context}

**Instructions**:
1. Directly address the question using the provided data
2. Highlight key metrics relevant to the question
3. Integrate insights from recent news where applicable
4. Provide a clear, structured response (use sections if helpful)
5. Be concise but comprehensive (aim for 200-300 words)

**Response**:
""".strip()

        return system_prompt, user_prompt

    @staticmethod
    def build_comparison_prompt(
        ticker1: str,
        ticker2: str,
        question: str,
        financial_data1: dict[str, Any],
        financial_data2: dict[str, Any],
        context1: str,
        context2: str,
    ) -> tuple[str, str]:
        """
        Build prompt for comparing two tickers.

        Args:
            ticker1: First ticker
            ticker2: Second ticker
            question: User question
            financial_data1: Financial data for ticker1
            financial_data2: Financial data for ticker2
            context1: Context for ticker1
            context2: Context for ticker2

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = PromptBuilder.SYSTEM_PROMPTS["comparative_analyst"]

        summary1 = PromptBuilder._format_financial_data(financial_data1)
        summary2 = PromptBuilder._format_financial_data(financial_data2)

        user_prompt = f"""
Compare {ticker1} and {ticker2} based on the question below.

**Question**: {question}

**{ticker1} Financial Data**:
{summary1}

**{ticker1} Recent Context**:
{context1}

---

**{ticker2} Financial Data**:
{summary2}

**{ticker2} Recent Context**:
{context2}

**Instructions**:
1. Provide a structured comparison addressing the question
2. Compare key metrics side-by-side (create a mental table if helpful)
3. Explain differences in context (business model, sector, maturity)
4. Highlight relative strengths and weaknesses
5. Integrate qualitative factors from news
6. Keep response focused and concise (300-400 words)

**Response**:
""".strip()

        return system_prompt, user_prompt

    @staticmethod
    def build_risk_analysis_prompt(
        ticker: str, financial_data: dict[str, Any], context: str
    ) -> tuple[str, str]:
        """
        Build prompt for risk analysis.

        Args:
            ticker: Stock ticker
            financial_data: Dictionary of financial metrics
            context: Retrieved textual context

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = PromptBuilder.SYSTEM_PROMPTS["risk_analyst"]

        financial_summary = PromptBuilder._format_financial_data(financial_data)

        user_prompt = f"""
Conduct a risk assessment for {ticker} based on financial data and recent news.

**Financial Data**:
{financial_summary}

**Recent News & Context**:
{context}

**Instructions**:
Identify and analyze the key risks for {ticker} across these categories:

1. **Financial Risks**: Leverage, liquidity, profitability pressure
2. **Business Risks**: Competition, market dynamics, execution
3. **External Risks**: Regulation, macro environment, geopolitics

For each risk:
- Describe the risk clearly
- Assess magnitude (High/Medium/Low)
- Support with data or news references

Keep response structured and concise (250-350 words).

**Risk Assessment**:
""".strip()

        return system_prompt, user_prompt

    @staticmethod
    def build_general_prompt(
        question: str, context: str, financial_data: dict[str, Any] | None = None
    ) -> tuple[str, str]:
        """
        Build general analysis prompt.

        Args:
            question: User question
            context: Retrieved textual context
            financial_data: Optional financial data

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = PromptBuilder.SYSTEM_PROMPTS["equity_analyst"]

        financial_section = ""
        if financial_data:
            financial_summary = PromptBuilder._format_financial_data(financial_data)
            financial_section = f"""
**Financial Data**:
{financial_summary}
"""

        user_prompt = f"""
Answer the following question based on the provided context.

**Question**: {question}
{financial_section}
**Context**:
{context}

**Instructions**:
1. Provide a clear, direct answer to the question
2. Use data and context to support your response
3. Be analytical and objective
4. Structure your response logically
5. Keep it concise (200-300 words)

**Response**:
""".strip()

        return system_prompt, user_prompt

    @staticmethod
    def _format_financial_data(data: dict[str, Any]) -> str:
        """
        Format financial data dictionary into readable text.

        Args:
            data: Dictionary of financial metrics

        Returns:
            Formatted string
        """
        sections = []

        # Basic info
        ticker = data.get("ticker", "N/A")
        period = data.get("period", "N/A")
        sector = data.get("sector", "N/A")

        sections.append(f"Ticker: {ticker} | Period: {period} | Sector: {sector}")

        # Income statement metrics
        income_metrics = []
        if data.get("revenue"):
            income_metrics.append(f"  Revenue: ${data['revenue']:,.0f}M")
        if data.get("net_income"):
            income_metrics.append(f"  Net Income: ${data['net_income']:,.0f}M")
        if data.get("ebitda"):
            income_metrics.append(f"  EBITDA: ${data['ebitda']:,.0f}M")

        if income_metrics:
            sections.append("\nIncome Statement:\n" + "\n".join(income_metrics))

        # Margins
        margin_metrics = []
        for margin_key in ["gross_margin", "operating_margin", "ebitda_margin", "net_margin"]:
            value = data.get(margin_key)
            if value is not None:
                label = margin_key.replace("_", " ").title()
                margin_metrics.append(f"  {label}: {value:.1f}%")

        if margin_metrics:
            sections.append("\nProfitability Margins:\n" + "\n".join(margin_metrics))

        # Returns
        return_metrics = []
        for return_key in ["roe", "roa", "roic"]:
            value = data.get(return_key)
            if value is not None:
                label = return_key.upper()
                return_metrics.append(f"  {label}: {value:.1f}%")

        if return_metrics:
            sections.append("\nReturns:\n" + "\n".join(return_metrics))

        # Balance sheet
        balance_metrics = []
        if data.get("total_assets"):
            balance_metrics.append(f"  Total Assets: ${data['total_assets']:,.0f}M")
        if data.get("equity"):
            balance_metrics.append(f"  Equity: ${data['equity']:,.0f}M")
        if data.get("net_debt"):
            balance_metrics.append(f"  Net Debt: ${data['net_debt']:,.0f}M")

        if balance_metrics:
            sections.append("\nBalance Sheet:\n" + "\n".join(balance_metrics))

        # Leverage
        leverage_metrics = []
        if data.get("debt_to_equity") is not None:
            leverage_metrics.append(f"  Debt/Equity: {data['debt_to_equity']:.2f}x")
        if data.get("net_debt_to_ebitda") is not None:
            leverage_metrics.append(f"  Net Debt/EBITDA: {data['net_debt_to_ebitda']:.2f}x")

        if leverage_metrics:
            sections.append("\nLeverage:\n" + "\n".join(leverage_metrics))

        # Growth
        growth_metrics = []
        if data.get("revenue_growth_yoy") is not None:
            growth_metrics.append(f"  Revenue Growth YoY: {data['revenue_growth_yoy']:.1f}%")
        if data.get("net_income_growth_yoy") is not None:
            growth_metrics.append(
                f"  Net Income Growth YoY: {data['net_income_growth_yoy']:.1f}%"
            )

        if growth_metrics:
            sections.append("\nGrowth:\n" + "\n".join(growth_metrics))

        # Per share
        per_share_metrics = []
        if data.get("eps") is not None:
            per_share_metrics.append(f"  EPS: ${data['eps']:.2f}")
        if data.get("book_value_per_share") is not None:
            per_share_metrics.append(
                f"  Book Value Per Share: ${data['book_value_per_share']:.2f}"
            )

        if per_share_metrics:
            sections.append("\nPer Share Metrics:\n" + "\n".join(per_share_metrics))

        return "\n".join(sections)


if __name__ == "__main__":
    # Test prompt building
    print("Testing Prompt Builder\n" + "=" * 80)

    # Sample financial data
    sample_data = {
        "ticker": "AAPL",
        "period": "2024-Q4",
        "sector": "Technology",
        "revenue": 94930,
        "net_income": 22956,
        "ebitda": 32180,
        "equity": 74100,
        "total_assets": 364980,
        "net_debt": -52840,
        "net_margin": 24.2,
        "operating_margin": 32.4,
        "roe": 31.0,
        "roa": 6.3,
        "debt_to_equity": -0.71,
        "revenue_growth_yoy": 6.1,
        "eps": 1.64,
    }

    context = "Apple reported strong Q4 results with revenue up 6% YoY..."

    # Test single ticker prompt
    print("\n1. Single Ticker Analysis Prompt:")
    print("-" * 80)
    system, user = PromptBuilder.build_single_ticker_analysis_prompt(
        "AAPL",
        "What are the key takeaways from recent earnings?",
        sample_data,
        context,
    )
    print(f"System: {system[:100]}...")
    print(f"\nUser:\n{user[:500]}...")

    # Test comparison prompt
    print("\n\n2. Comparison Prompt:")
    print("-" * 80)
    system, user = PromptBuilder.build_comparison_prompt(
        "AAPL", "MSFT", "Which company has better profitability?", sample_data, sample_data, context, context
    )
    print(f"User:\n{user[:500]}...")

    # Test risk analysis prompt
    print("\n\n3. Risk Analysis Prompt:")
    print("-" * 80)
    system, user = PromptBuilder.build_risk_analysis_prompt("AAPL", sample_data, context)
    print(f"User:\n{user[:500]}...")
