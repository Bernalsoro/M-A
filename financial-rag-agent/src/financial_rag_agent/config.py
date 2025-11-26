"""
Configuration management for the Financial RAG Agent.

Uses pydantic-settings for environment variable management and validation.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "data")
    vector_store_path: Path = Field(
        default_factory=lambda: Path(__file__).parent / "data" / "vector_store"
    )

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic"] = Field(
        default="openai", description="LLM provider to use"
    )
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")

    # Model Selection
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229", description="Anthropic model name"
    )
    llm_temperature: float = Field(default=0.1, description="LLM sampling temperature")
    llm_max_tokens: int = Field(default=2048, description="Maximum tokens in LLM response")

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings",
    )
    embedding_dimension: int = Field(default=384, description="Embedding vector dimension")

    # Retrieval Configuration
    retrieval_top_k: int = Field(default=5, description="Number of documents to retrieve")
    retrieval_score_threshold: float = Field(
        default=0.5, description="Minimum similarity score for retrieval"
    )

    # Agent Configuration
    agent_max_iterations: int = Field(default=5, description="Maximum agent reasoning iterations")
    agent_enable_planning: bool = Field(default=True, description="Enable agent planning step")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_cors_origins: list[str] = Field(
        default=["http://localhost:3000"], description="CORS allowed origins"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    def get_llm_api_key(self) -> str | None:
        """Get the appropriate API key based on selected provider."""
        if self.llm_provider == "openai":
            return self.openai_api_key
        elif self.llm_provider == "anthropic":
            return self.anthropic_api_key
        return None

    def get_llm_model(self) -> str:
        """Get the appropriate model name based on selected provider."""
        if self.llm_provider == "openai":
            return self.openai_model
        elif self.llm_provider == "anthropic":
            return self.anthropic_model
        raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    @property
    def financials_path(self) -> Path:
        """Path to financial data CSV."""
        return self.data_dir / "sample_financials.csv"

    @property
    def news_path(self) -> Path:
        """Path to news data JSON."""
        return self.data_dir / "sample_news.json"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection function for FastAPI."""
    return settings
