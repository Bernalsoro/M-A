"""Data ingestion module for loading and preprocessing financial data."""

from financial_rag_agent.ingestion.loader import DataLoader
from financial_rag_agent.ingestion.preprocessor import FinancialPreprocessor

__all__ = ["DataLoader", "FinancialPreprocessor"]
