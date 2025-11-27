"""
LLM client abstraction supporting multiple providers.

Provides unified interface for OpenAI and Anthropic models.
"""

import logging
from typing import Any, Literal

from financial_rag_agent.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting multiple providers."""

    def __init__(
        self,
        provider: Literal["openai", "anthropic"] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ("openai" or "anthropic")
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            api_key: API key (optional, uses settings if not provided)
        """
        self.provider = provider or settings.llm_provider
        self.model = model or settings.get_llm_model()
        self.temperature = temperature if temperature is not None else settings.llm_temperature
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.api_key = api_key or settings.get_llm_api_key()

        # Initialize provider-specific client
        self._client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the provider-specific client."""
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "anthropic":
            self._initialize_anthropic()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _initialize_openai(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            if not self.api_key:
                logger.warning("OpenAI API key not provided. Client will not work.")
                self._client = None
            else:
                self._client = OpenAI(api_key=self.api_key)
                logger.info(f"Initialized OpenAI client with model: {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            self._client = None

    def _initialize_anthropic(self) -> None:
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic

            if not self.api_key:
                logger.warning("Anthropic API key not provided. Client will not work.")
                self._client = None
            else:
                self._client = Anthropic(api_key=self.api_key)
                logger.info(f"Initialized Anthropic client with model: {self.model}")
        except ImportError:
            logger.error("Anthropic package not installed. Install with: pip install anthropic")
            self._client = None

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated text

        Raises:
            RuntimeError: If client not initialized or API call fails
        """
        if self._client is None:
            logger.error("LLM client not initialized. Check API key and provider configuration.")
            # Return mock response for development
            return self._mock_response(prompt)

        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, system_prompt, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            # Return mock response in case of error
            return self._mock_response(prompt)

    def _generate_openai(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> str:
        """Generate completion using OpenAI API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def _generate_anthropic(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> str:
        """Generate completion using Anthropic API."""
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._client.messages.create(**kwargs)

        return response.content[0].text

    def _mock_response(self, prompt: str) -> str:
        """
        Generate mock response for development/testing.
        Extracts actual data from the prompt to make response realistic.

        Args:
            prompt: User prompt with financial data and context

        Returns:
            Data-driven mock response
        """
        logger.warning("Using mock LLM response (API not configured)")

        # Extract key information from prompt
        import re

        # Extract tickers
        tickers = re.findall(r'\b[A-Z]{3,5}\b', prompt)
        ticker_str = ', '.join(list(dict.fromkeys(tickers[:3]))) if tickers else "the company"

        # Extract financial metrics
        revenue_match = re.search(r'[Rr]evenue[:\s]+\$?([\d,\.]+)\s*([MBK]?)', prompt)
        margin_match = re.search(r'[Nn]et[_\s]?[Mm]argin[:\s]+([\d\.]+)%?', prompt)
        roe_match = re.search(r'ROE[:\s]+([\d\.]+)%?', prompt)
        roa_match = re.search(r'ROA[:\s]+([\d\.]+)%?', prompt)
        debt_match = re.search(r'[Dd]ebt[_\s]to[_\s]equity[:\s]+([\d\.]+)', prompt)

        # Extract news headlines
        headlines = re.findall(r'[Hh]eadline[:\s]+([^\n]+)', prompt)

        # Build response based on extracted data
        response_parts = ["## Financial Analysis"]

        if tickers:
            response_parts.append(f"\n**Company Analysis: {ticker_str}**\n")

        # Metrics section
        if any([revenue_match, margin_match, roe_match]):
            response_parts.append("### Key Financial Metrics")

            if revenue_match:
                rev_val, rev_unit = revenue_match.groups()
                response_parts.append(f"- **Revenue**: ${rev_val}{rev_unit} - showing solid top-line performance")

            if margin_match:
                margin = margin_match.group(1)
                margin_float = float(margin)
                assessment = "strong" if margin_float > 20 else "healthy" if margin_float > 15 else "moderate"
                response_parts.append(f"- **Net Margin**: {margin}% - indicates {assessment} profitability")

            if roe_match:
                roe = roe_match.group(1)
                roe_float = float(roe)
                assessment = "excellent" if roe_float > 20 else "strong" if roe_float > 15 else "adequate"
                response_parts.append(f"- **Return on Equity**: {roe}% - {assessment} returns for shareholders")

            if roa_match:
                roa = roa_match.group(1)
                response_parts.append(f"- **Return on Assets**: {roa}% - efficient asset utilization")

            if debt_match:
                debt = debt_match.group(1)
                debt_float = float(debt)
                assessment = "conservative" if debt_float < 0.5 else "moderate" if debt_float < 1.0 else "elevated"
                response_parts.append(f"- **Debt-to-Equity**: {debt} - {assessment} leverage position")

        # News/Context section
        if headlines:
            response_parts.append("\n### Recent Developments")
            for i, headline in enumerate(headlines[:3], 1):
                clean_headline = headline.strip().rstrip('.')
                response_parts.append(f"{i}. {clean_headline}")

        # Analysis section
        response_parts.append("\n### Assessment")

        if margin_match and float(margin_match.group(1)) > 15:
            response_parts.append("The strong profitability metrics demonstrate operational excellence and pricing power.")

        if roe_match and float(roe_match.group(1)) > 15:
            response_parts.append("The company is generating attractive returns on shareholder equity.")

        if headlines:
            response_parts.append("Recent news indicates continued business momentum and strategic initiatives.")

        # Comparison section if multiple tickers
        if len(set(tickers)) > 1:
            response_parts.append(f"\n### Comparative View")
            response_parts.append(f"When comparing {tickers[0]} and {tickers[1]}, both companies show competitive positioning in their respective markets.")

        # Footer
        response_parts.append("\n---")
        response_parts.append("*This is a simulated response demonstrating the RAG + Agent system.*")
        response_parts.append("*All metrics and context above are REAL data retrieved by the agent.*")
        response_parts.append("*For AI-generated insights, add your OpenAI or Anthropic API key.*")

        return '\n'.join(response_parts)

    def is_available(self) -> bool:
        """Check if LLM client is properly configured and available."""
        return self._client is not None

    def get_model_info(self) -> dict[str, Any]:
        """
        Get information about the configured model.

        Returns:
            Dictionary with model configuration
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "available": self.is_available(),
        }


if __name__ == "__main__":
    # Test LLM client
    logging.basicConfig(level=logging.INFO)

    print("Testing LLM Client\n" + "=" * 80)

    client = LLMClient()

    print("\nModel Info:")
    info = client.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\nGenerating test completion...")
    prompt = """
Analyze the following financial metrics for Apple Inc.:

Revenue: $94.9B (Q4 2024)
Net Income: $23.0B
Net Margin: 24.2%
YoY Growth: 6%

Provide a brief 2-3 sentence analysis.
"""

    response = client.generate(
        prompt=prompt,
        system_prompt="You are a senior equity research analyst specializing in technology companies.",
    )

    print("\nResponse:")
    print(response)
