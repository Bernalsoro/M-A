"""
Análisis de Múltiplos (Trading Comparables)

Valoración basada en comparables de mercado usando múltiplos como:
- EV/EBITDA
- EV/Revenue
- P/E (Price to Earnings)
- P/B (Price to Book)
- EV/EBIT
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Optional, Literal
import numpy as np
from utils.data_validation import validate_positive


class MultiplesAnalysis:
    """
    Análisis de valoración por múltiplos de empresas comparables

    Calcula múltiplos de mercado de empresas comparables y los aplica
    a las métricas de la empresa objetivo para determinar su valoración.
    """

    def __init__(self):
        """Inicializa el análisis de múltiplos"""
        self.comparables = []

    def add_comparable(
        self,
        name: str,
        market_cap: Optional[float] = None,
        enterprise_value: Optional[float] = None,
        revenue: Optional[float] = None,
        ebitda: Optional[float] = None,
        ebit: Optional[float] = None,
        net_income: Optional[float] = None,
        book_value: Optional[float] = None,
        description: str = ""
    ):
        """
        Añade una empresa comparable

        Args:
            name: Nombre de la empresa
            market_cap: Capitalización de mercado
            enterprise_value: Enterprise Value (Market Cap + Net Debt)
            revenue: Ingresos
            ebitda: EBITDA
            ebit: EBIT
            net_income: Beneficio neto
            book_value: Valor en libros
            description: Descripción opcional
        """
        comparable = {
            'name': name,
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'revenue': revenue,
            'ebitda': ebitda,
            'ebit': ebit,
            'net_income': net_income,
            'book_value': book_value,
            'description': description
        }

        # Calcular múltiplos
        comparable['multiples'] = self._calculate_multiples(comparable)

        self.comparables.append(comparable)

    def _calculate_multiples(self, company: dict) -> dict:
        """
        Calcula todos los múltiplos posibles para una empresa

        Args:
            company: Diccionario con datos financieros de la empresa

        Returns:
            Diccionario con múltiplos calculados
        """
        multiples = {}

        # EV-based multiples
        if company['enterprise_value']:
            ev = company['enterprise_value']

            if company['revenue']:
                multiples['ev_revenue'] = ev / company['revenue']

            if company['ebitda'] and company['ebitda'] > 0:
                multiples['ev_ebitda'] = ev / company['ebitda']

            if company['ebit'] and company['ebit'] > 0:
                multiples['ev_ebit'] = ev / company['ebit']

        # Market Cap-based multiples
        if company['market_cap']:
            mc = company['market_cap']

            if company['revenue']:
                multiples['p_revenue'] = mc / company['revenue']

            if company['net_income'] and company['net_income'] > 0:
                multiples['pe'] = mc / company['net_income']

            if company['book_value'] and company['book_value'] > 0:
                multiples['pb'] = mc / company['book_value']

        return multiples

    def get_comparable_multiples(
        self,
        multiple_type: Literal[
            'ev_revenue', 'ev_ebitda', 'ev_ebit', 'p_revenue', 'pe', 'pb'
        ]
    ) -> Dict:
        """
        Obtiene estadísticas de un múltiplo específico de todos los comparables

        Args:
            multiple_type: Tipo de múltiplo a analizar

        Returns:
            Diccionario con estadísticas (mean, median, min, max, etc.)
        """
        values = []

        for comp in self.comparables:
            if multiple_type in comp['multiples']:
                value = comp['multiples'][multiple_type]
                if value is not None and not np.isnan(value) and not np.isinf(value):
                    values.append(value)

        if not values:
            return {
                'count': 0,
                'mean': None,
                'median': None,
                'min': None,
                'max': None,
                'std': None
            }

        return {
            'count': len(values),
            'mean': np.mean(values),
            'median': np.median(values),
            'min': np.min(values),
            'max': np.max(values),
            'std': np.std(values),
            'values': values
        }

    def calculate_valuation(
        self,
        target_revenue: Optional[float] = None,
        target_ebitda: Optional[float] = None,
        target_ebit: Optional[float] = None,
        target_net_income: Optional[float] = None,
        target_book_value: Optional[float] = None,
        statistic: Literal['mean', 'median'] = 'median',
        net_debt: float = 0,
        shares_outstanding: Optional[float] = None
    ) -> Dict:
        """
        Calcula la valoración del target usando múltiplos comparables

        Args:
            target_revenue: Revenue del target
            target_ebitda: EBITDA del target
            target_ebit: EBIT del target
            target_net_income: Net Income del target
            target_book_value: Book Value del target
            statistic: Usar 'mean' o 'median' de comparables
            net_debt: Deuda neta del target
            shares_outstanding: Acciones en circulación

        Returns:
            Diccionario con valoraciones por cada múltiplo
        """
        valuations = {}

        # EV-based valuations
        if target_revenue:
            stats = self.get_comparable_multiples('ev_revenue')
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_revenue * multiple
                equity_value = ev - net_debt

                valuations['ev_revenue'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_revenue,
                    'comparables_count': stats['count']
                }

        if target_ebitda and target_ebitda > 0:
            stats = self.get_comparable_multiples('ev_ebitda')
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_ebitda * multiple
                equity_value = ev - net_debt

                valuations['ev_ebitda'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_ebitda,
                    'comparables_count': stats['count']
                }

        if target_ebit and target_ebit > 0:
            stats = self.get_comparable_multiples('ev_ebit')
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_ebit * multiple
                equity_value = ev - net_debt

                valuations['ev_ebit'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_ebit,
                    'comparables_count': stats['count']
                }

        # Market Cap-based valuations
        if target_net_income and target_net_income > 0:
            stats = self.get_comparable_multiples('pe')
            if stats['count'] > 0:
                multiple = stats[statistic]
                equity_value = target_net_income * multiple

                valuations['pe'] = {
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_net_income,
                    'comparables_count': stats['count']
                }

        if target_book_value and target_book_value > 0:
            stats = self.get_comparable_multiples('pb')
            if stats['count'] > 0:
                multiple = stats[statistic]
                equity_value = target_book_value * multiple

                valuations['pb'] = {
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_book_value,
                    'comparables_count': stats['count']
                }

        # Calcular valor por acción si se proporciona
        if shares_outstanding:
            for method in valuations:
                if 'equity_value' in valuations[method]:
                    valuations[method]['value_per_share'] = \
                        valuations[method]['equity_value'] / shares_outstanding

        # Calcular valoración promedio
        equity_values = [v['equity_value'] for v in valuations.values()
                        if 'equity_value' in v]

        if equity_values:
            avg_equity_value = np.mean(equity_values)
            valuations['average'] = {
                'equity_value': avg_equity_value,
                'methods_count': len(equity_values)
            }

            if shares_outstanding:
                valuations['average']['value_per_share'] = \
                    avg_equity_value / shares_outstanding

        return valuations

    def football_field_analysis(
        self,
        target_revenue: Optional[float] = None,
        target_ebitda: Optional[float] = None,
        target_ebit: Optional[float] = None,
        target_net_income: Optional[float] = None,
        net_debt: float = 0,
        shares_outstanding: Optional[float] = None
    ) -> Dict:
        """
        Análisis tipo "Football Field" mostrando rangos de valoración

        Args:
            target_revenue: Revenue del target
            target_ebitda: EBITDA del target
            target_ebit: EBIT del target
            target_net_income: Net Income del target
            net_debt: Deuda neta del target
            shares_outstanding: Acciones en circulación

        Returns:
            Diccionario con rangos min-max de valoración por método
        """
        ranges = {}

        # Para cada múltiplo, calcular rango usando min-max de comparables
        if target_revenue:
            stats = self.get_comparable_multiples('ev_revenue')
            if stats['count'] > 0:
                ev_min = target_revenue * stats['min']
                ev_max = target_revenue * stats['max']
                ranges['ev_revenue'] = {
                    'min_enterprise_value': ev_min,
                    'max_enterprise_value': ev_max,
                    'min_equity_value': ev_min - net_debt,
                    'max_equity_value': ev_max - net_debt,
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_ebitda and target_ebitda > 0:
            stats = self.get_comparable_multiples('ev_ebitda')
            if stats['count'] > 0:
                ev_min = target_ebitda * stats['min']
                ev_max = target_ebitda * stats['max']
                ranges['ev_ebitda'] = {
                    'min_enterprise_value': ev_min,
                    'max_enterprise_value': ev_max,
                    'min_equity_value': ev_min - net_debt,
                    'max_equity_value': ev_max - net_debt,
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_ebit and target_ebit > 0:
            stats = self.get_comparable_multiples('ev_ebit')
            if stats['count'] > 0:
                ev_min = target_ebit * stats['min']
                ev_max = target_ebit * stats['max']
                ranges['ev_ebit'] = {
                    'min_enterprise_value': ev_min,
                    'max_enterprise_value': ev_max,
                    'min_equity_value': ev_min - net_debt,
                    'max_equity_value': ev_max - net_debt,
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_net_income and target_net_income > 0:
            stats = self.get_comparable_multiples('pe')
            if stats['count'] > 0:
                ranges['pe'] = {
                    'min_equity_value': target_net_income * stats['min'],
                    'max_equity_value': target_net_income * stats['max'],
                    'multiple_range': (stats['min'], stats['max'])
                }

        # Calcular valor por acción
        if shares_outstanding:
            for method in ranges:
                if 'min_equity_value' in ranges[method]:
                    ranges[method]['min_value_per_share'] = \
                        ranges[method]['min_equity_value'] / shares_outstanding
                    ranges[method]['max_value_per_share'] = \
                        ranges[method]['max_equity_value'] / shares_outstanding

        return ranges

    def get_summary(self) -> Dict:
        """
        Obtiene un resumen de todos los comparables y sus múltiplos

        Returns:
            Diccionario con resumen de múltiplos
        """
        summary = {
            'total_comparables': len(self.comparables),
            'multiples_statistics': {}
        }

        multiple_types = ['ev_revenue', 'ev_ebitda', 'ev_ebit', 'p_revenue', 'pe', 'pb']

        for mult_type in multiple_types:
            stats = self.get_comparable_multiples(mult_type)
            if stats['count'] > 0:
                summary['multiples_statistics'][mult_type] = stats

        return summary

    def __repr__(self) -> str:
        """Representación en string del análisis"""
        return (
            f"MultiplesAnalysis(\n"
            f"  Comparables: {len(self.comparables)}\n"
            f"  Companies: {[c['name'] for c in self.comparables]}\n"
            f")"
        )
