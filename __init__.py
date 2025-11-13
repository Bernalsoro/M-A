"""
M&A Valuation Tools

Professional valuation toolkit for Mergers & Acquisitions
"""

__version__ = "1.0.0"
__author__ = "M&A Team"

from models.dcf import DCFModel
from models.multiples import MultiplesAnalysis
from models.precedent_transactions import PrecedentTransactionsAnalysis
from models.synergies import SynergiesModel
from models.lbo import LBOModel
from models.integration_value_creation import IntegrationValueCreation
from analysis.financial_ratios import FinancialRatiosAnalysis
from analysis.due_diligence import DueDiligenceAnalysis

__all__ = [
    'DCFModel',
    'MultiplesAnalysis',
    'PrecedentTransactionsAnalysis',
    'SynergiesModel',
    'LBOModel',
    'IntegrationValueCreation',
    'FinancialRatiosAnalysis',
    'DueDiligenceAnalysis',
]
