"""
Análisis de Ratios Financieros

KPIs clave para M&A:
- ROIC (Return on Invested Capital)
- ROE, ROA
- Márgenes (Gross, EBITDA, Operating, Net)
- Leverage ratios
- Efficiency ratios
- Liquidez
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Optional, List
import numpy as np
from utils.data_validation import validate_positive


class FinancialRatiosAnalysis:
    """
    Análisis completo de ratios financieros para M&A

    Calcula y analiza KPIs clave para evaluación de targets
    """

    def __init__(self):
        """Inicializa el análisis de ratios"""
        self.periods = []

    def add_period(
        self,
        period_name: str,
        revenue: float,
        cogs: Optional[float] = None,
        gross_profit: Optional[float] = None,
        ebitda: Optional[float] = None,
        ebit: Optional[float] = None,
        operating_income: Optional[float] = None,
        net_income: Optional[float] = None,
        total_assets: Optional[float] = None,
        current_assets: Optional[float] = None,
        current_liabilities: Optional[float] = None,
        total_equity: Optional[float] = None,
        total_debt: Optional[float] = None,
        cash: Optional[float] = None,
        inventory: Optional[float] = None,
        accounts_receivable: Optional[float] = None,
        accounts_payable: Optional[float] = None,
        capex: Optional[float] = None,
        depreciation: Optional[float] = None,
        interest_expense: Optional[float] = None
    ):
        """
        Añade datos de un período

        Args:
            period_name: Nombre del período (ej: "2023", "Q4 2023")
            revenue: Ingresos
            cogs: Coste de bienes vendidos
            gross_profit: Beneficio bruto
            ebitda: EBITDA
            ebit: EBIT
            operating_income: Resultado operativo
            net_income: Beneficio neto
            total_assets: Activos totales
            current_assets: Activos corrientes
            current_liabilities: Pasivos corrientes
            total_equity: Patrimonio neto
            total_debt: Deuda total
            cash: Efectivo y equivalentes
            inventory: Inventario
            accounts_receivable: Cuentas por cobrar
            accounts_payable: Cuentas por pagar
            capex: CapEx
            depreciation: Depreciación y amortización
            interest_expense: Gastos financieros
        """
        period_data = {
            'period_name': period_name,
            'revenue': validate_positive(revenue, "Revenue"),
            'cogs': cogs,
            'gross_profit': gross_profit if gross_profit is not None else (revenue - cogs if cogs else None),
            'ebitda': ebitda,
            'ebit': ebit,
            'operating_income': operating_income,
            'net_income': net_income,
            'total_assets': total_assets,
            'current_assets': current_assets,
            'current_liabilities': current_liabilities,
            'total_equity': total_equity,
            'total_debt': total_debt,
            'cash': cash,
            'inventory': inventory,
            'accounts_receivable': accounts_receivable,
            'accounts_payable': accounts_payable,
            'capex': capex,
            'depreciation': depreciation,
            'interest_expense': interest_expense
        }

        self.periods.append(period_data)

    def calculate_profitability_ratios(self, period_index: int = -1) -> Dict:
        """
        Calcula ratios de rentabilidad

        Args:
            period_index: Índice del período (-1 para el más reciente)

        Returns:
            Diccionario con ratios de rentabilidad
        """
        period = self.periods[period_index]
        ratios = {}

        # Margins
        if period['gross_profit'] is not None:
            ratios['gross_margin'] = period['gross_profit'] / period['revenue']

        if period['ebitda'] is not None:
            ratios['ebitda_margin'] = period['ebitda'] / period['revenue']

        if period['ebit'] is not None:
            ratios['ebit_margin'] = period['ebit'] / period['revenue']

        if period['operating_income'] is not None:
            ratios['operating_margin'] = period['operating_income'] / period['revenue']

        if period['net_income'] is not None:
            ratios['net_margin'] = period['net_income'] / period['revenue']

        # Return ratios
        if period['total_assets'] and period['net_income']:
            ratios['roa'] = period['net_income'] / period['total_assets']

        if period['total_equity'] and period['net_income']:
            ratios['roe'] = period['net_income'] / period['total_equity']

        # ROIC (Return on Invested Capital)
        if all([period['ebit'], period['total_assets'], period['current_liabilities']]):
            # ROIC = NOPAT / Invested Capital
            # Asumir tax rate de 25% si no disponible
            tax_rate = 0.25
            nopat = period['ebit'] * (1 - tax_rate)
            invested_capital = period['total_assets'] - period['current_liabilities']
            ratios['roic'] = nopat / invested_capital if invested_capital > 0 else None

        return {
            'period': period['period_name'],
            'ratios': ratios
        }

    def calculate_leverage_ratios(self, period_index: int = -1) -> Dict:
        """
        Calcula ratios de apalancamiento

        Args:
            period_index: Índice del período

        Returns:
            Ratios de leverage
        """
        period = self.periods[period_index]
        ratios = {}

        if period['total_debt'] and period['total_equity']:
            ratios['debt_to_equity'] = period['total_debt'] / period['total_equity']

        if period['total_debt'] and period['total_assets']:
            ratios['debt_to_assets'] = period['total_debt'] / period['total_assets']

        if period['total_debt'] and period['ebitda']:
            ratios['debt_to_ebitda'] = period['total_debt'] / period['ebitda']

        if period['ebitda'] and period['interest_expense']:
            ratios['interest_coverage'] = period['ebitda'] / period['interest_expense']

        if period['total_debt'] and period['cash']:
            ratios['net_debt'] = period['total_debt'] - period['cash']
            if period['ebitda']:
                ratios['net_debt_to_ebitda'] = ratios['net_debt'] / period['ebitda']

        return {
            'period': period['period_name'],
            'ratios': ratios
        }

    def calculate_liquidity_ratios(self, period_index: int = -1) -> Dict:
        """
        Calcula ratios de liquidez

        Args:
            period_index: Índice del período

        Returns:
            Ratios de liquidez
        """
        period = self.periods[period_index]
        ratios = {}

        if period['current_assets'] and period['current_liabilities']:
            ratios['current_ratio'] = period['current_assets'] / period['current_liabilities']

            # Quick ratio (excluye inventario)
            if period['inventory']:
                quick_assets = period['current_assets'] - period['inventory']
                ratios['quick_ratio'] = quick_assets / period['current_liabilities']

        if period['cash'] and period['current_liabilities']:
            ratios['cash_ratio'] = period['cash'] / period['current_liabilities']

        return {
            'period': period['period_name'],
            'ratios': ratios
        }

    def calculate_efficiency_ratios(self, period_index: int = -1) -> Dict:
        """
        Calcula ratios de eficiencia operativa

        Args:
            period_index: Índice del período

        Returns:
            Ratios de eficiencia
        """
        period = self.periods[period_index]
        ratios = {}

        if period['revenue'] and period['total_assets']:
            ratios['asset_turnover'] = period['revenue'] / period['total_assets']

        # Days Sales Outstanding (DSO)
        if period['accounts_receivable'] and period['revenue']:
            ratios['dso'] = (period['accounts_receivable'] / period['revenue']) * 365

        # Days Inventory Outstanding (DIO)
        if period['inventory'] and period['cogs']:
            ratios['dio'] = (period['inventory'] / period['cogs']) * 365

        # Days Payable Outstanding (DPO)
        if period['accounts_payable'] and period['cogs']:
            ratios['dpo'] = (period['accounts_payable'] / period['cogs']) * 365

        # Cash Conversion Cycle
        if all(k in ratios for k in ['dso', 'dio', 'dpo']):
            ratios['cash_conversion_cycle'] = ratios['dso'] + ratios['dio'] - ratios['dpo']

        return {
            'period': period['period_name'],
            'ratios': ratios
        }

    def calculate_growth_metrics(self) -> Dict:
        """
        Calcula métricas de crecimiento (requiere múltiples períodos)

        Returns:
            Métricas de crecimiento
        """
        if len(self.periods) < 2:
            return {'error': 'Se requieren al menos 2 períodos'}

        growth_metrics = {}

        # Revenue growth
        revenues = [p['revenue'] for p in self.periods]
        growth_metrics['revenue_growth'] = [
            (revenues[i] / revenues[i-1] - 1) if revenues[i-1] > 0 else None
            for i in range(1, len(revenues))
        ]

        # EBITDA growth
        ebitdas = [p['ebitda'] for p in self.periods if p['ebitda'] is not None]
        if len(ebitdas) >= 2:
            growth_metrics['ebitda_growth'] = [
                (ebitdas[i] / ebitdas[i-1] - 1) if ebitdas[i-1] > 0 else None
                for i in range(1, len(ebitdas))
            ]

        # Net Income growth
        net_incomes = [p['net_income'] for p in self.periods if p['net_income'] is not None]
        if len(net_incomes) >= 2:
            growth_metrics['net_income_growth'] = [
                (net_incomes[i] / net_incomes[i-1] - 1) if net_incomes[i-1] > 0 else None
                for i in range(1, len(net_incomes))
            ]

        # CAGR calculations
        if len(revenues) >= 2:
            years = len(revenues) - 1
            growth_metrics['revenue_cagr'] = (revenues[-1] / revenues[0]) ** (1/years) - 1

        if len(ebitdas) >= 2:
            years = len(ebitdas) - 1
            growth_metrics['ebitda_cagr'] = (ebitdas[-1] / ebitdas[0]) ** (1/years) - 1

        return growth_metrics

    def calculate_all_ratios(self, period_index: int = -1) -> Dict:
        """
        Calcula todos los ratios para un período

        Args:
            period_index: Índice del período

        Returns:
            Diccionario con todos los ratios
        """
        return {
            'period': self.periods[period_index]['period_name'],
            'profitability': self.calculate_profitability_ratios(period_index)['ratios'],
            'leverage': self.calculate_leverage_ratios(period_index)['ratios'],
            'liquidity': self.calculate_liquidity_ratios(period_index)['ratios'],
            'efficiency': self.calculate_efficiency_ratios(period_index)['ratios']
        }

    def benchmark_analysis(
        self,
        benchmark_ratios: Dict[str, tuple],
        period_index: int = -1
    ) -> Dict:
        """
        Compara ratios con benchmarks de la industria

        Args:
            benchmark_ratios: Dict con nombre del ratio y (percentil_25, mediana, percentil_75)
            period_index: Índice del período

        Returns:
            Análisis comparativo

        Example:
            >>> benchmarks = {
            ...     'ebitda_margin': (0.15, 0.20, 0.25),
            ...     'roic': (0.10, 0.15, 0.20),
            ...     'debt_to_ebitda': (2.0, 3.0, 4.0)
            ... }
            >>> analysis.benchmark_analysis(benchmarks)
        """
        all_ratios = self.calculate_all_ratios(period_index)

        # Flatten ratios
        flat_ratios = {}
        for category in ['profitability', 'leverage', 'liquidity', 'efficiency']:
            flat_ratios.update(all_ratios[category])

        comparison = {}

        for ratio_name, (p25, median, p75) in benchmark_ratios.items():
            if ratio_name in flat_ratios and flat_ratios[ratio_name] is not None:
                value = flat_ratios[ratio_name]

                if value < p25:
                    position = 'Below 25th percentile'
                elif value < median:
                    position = '25th-50th percentile'
                elif value < p75:
                    position = '50th-75th percentile'
                else:
                    position = 'Above 75th percentile'

                comparison[ratio_name] = {
                    'value': value,
                    'benchmark_p25': p25,
                    'benchmark_median': median,
                    'benchmark_p75': p75,
                    'position': position,
                    'vs_median': value - median
                }

        return comparison

    def __repr__(self) -> str:
        """Representación en string"""
        return (
            f"FinancialRatiosAnalysis(\n"
            f"  Periods: {len(self.periods)}\n"
            f"  Period Names: {[p['period_name'] for p in self.periods]}\n"
            f")"
        )
