"""
Análisis de Transacciones Precedentes

Valoración basada en múltiplos pagados en transacciones M&A comparables.
Similar al análisis de múltiplos pero usando transacciones reales de M&A.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Optional, Literal
from datetime import datetime
import numpy as np
from utils.data_validation import validate_positive


class PrecedentTransactionsAnalysis:
    """
    Análisis de transacciones precedentes (M&A comparables)

    Analiza múltiplos pagados en transacciones M&A anteriores
    para valorar una transacción objetivo.
    """

    def __init__(self):
        """Inicializa el análisis de transacciones precedentes"""
        self.transactions = []

    def add_transaction(
        self,
        target_name: str,
        acquirer_name: str,
        transaction_value: float,
        date: str,
        revenue: Optional[float] = None,
        ebitda: Optional[float] = None,
        ebit: Optional[float] = None,
        net_income: Optional[float] = None,
        book_value: Optional[float] = None,
        premium: Optional[float] = None,
        deal_type: Optional[Literal['cash', 'stock', 'mixed']] = None,
        synergies: Optional[float] = None,
        description: str = ""
    ):
        """
        Añade una transacción precedente

        Args:
            target_name: Nombre de la empresa adquirida
            acquirer_name: Nombre del comprador
            transaction_value: Valor de la transacción (Enterprise Value)
            date: Fecha de la transacción (YYYY-MM-DD)
            revenue: Revenue del target
            ebitda: EBITDA del target
            ebit: EBIT del target
            net_income: Net Income del target
            book_value: Book Value del target
            premium: Premium pagado sobre precio de mercado (%)
            deal_type: Tipo de transacción
            synergies: Sinergias estimadas/anunciadas
            description: Descripción de la transacción
        """
        transaction = {
            'target_name': target_name,
            'acquirer_name': acquirer_name,
            'transaction_value': validate_positive(transaction_value, "Transaction value"),
            'date': date,
            'revenue': revenue,
            'ebitda': ebitda,
            'ebit': ebit,
            'net_income': net_income,
            'book_value': book_value,
            'premium': premium,
            'deal_type': deal_type,
            'synergies': synergies,
            'description': description
        }

        # Calcular múltiplos
        transaction['multiples'] = self._calculate_multiples(transaction)

        # Calcular antigüedad de la transacción
        try:
            trans_date = datetime.strptime(date, '%Y-%m-%d')
            days_ago = (datetime.now() - trans_date).days
            transaction['days_ago'] = days_ago
            transaction['years_ago'] = days_ago / 365.25
        except:
            transaction['days_ago'] = None
            transaction['years_ago'] = None

        self.transactions.append(transaction)

    def _calculate_multiples(self, transaction: dict) -> dict:
        """
        Calcula múltiplos pagados en la transacción

        Args:
            transaction: Diccionario con datos de la transacción

        Returns:
            Diccionario con múltiplos
        """
        multiples = {}
        tv = transaction['transaction_value']

        if transaction['revenue']:
            multiples['ev_revenue'] = tv / transaction['revenue']

        if transaction['ebitda'] and transaction['ebitda'] > 0:
            multiples['ev_ebitda'] = tv / transaction['ebitda']

        if transaction['ebit'] and transaction['ebit'] > 0:
            multiples['ev_ebit'] = tv / transaction['ebit']

        if transaction['net_income'] and transaction['net_income'] > 0:
            multiples['ev_net_income'] = tv / transaction['net_income']

        if transaction['book_value'] and transaction['book_value'] > 0:
            multiples['ev_book_value'] = tv / transaction['book_value']

        return multiples

    def filter_transactions(
        self,
        max_years_old: Optional[float] = None,
        min_transaction_value: Optional[float] = None,
        max_transaction_value: Optional[float] = None,
        deal_type: Optional[str] = None
    ) -> List[dict]:
        """
        Filtra transacciones por criterios

        Args:
            max_years_old: Máximo años desde la transacción
            min_transaction_value: Valor mínimo de transacción
            max_transaction_value: Valor máximo de transacción
            deal_type: Tipo de transacción

        Returns:
            Lista de transacciones filtradas
        """
        filtered = self.transactions.copy()

        if max_years_old is not None:
            filtered = [t for t in filtered
                       if t['years_ago'] is not None and t['years_ago'] <= max_years_old]

        if min_transaction_value is not None:
            filtered = [t for t in filtered
                       if t['transaction_value'] >= min_transaction_value]

        if max_transaction_value is not None:
            filtered = [t for t in filtered
                       if t['transaction_value'] <= max_transaction_value]

        if deal_type is not None:
            filtered = [t for t in filtered
                       if t['deal_type'] == deal_type]

        return filtered

    def get_transaction_multiples(
        self,
        multiple_type: Literal['ev_revenue', 'ev_ebitda', 'ev_ebit',
                               'ev_net_income', 'ev_book_value'],
        filters: Optional[dict] = None
    ) -> Dict:
        """
        Obtiene estadísticas de un múltiplo de transacciones

        Args:
            multiple_type: Tipo de múltiplo
            filters: Filtros opcionales (max_years_old, etc.)

        Returns:
            Diccionario con estadísticas
        """
        if filters:
            transactions = self.filter_transactions(**filters)
        else:
            transactions = self.transactions

        values = []

        for trans in transactions:
            if multiple_type in trans['multiples']:
                value = trans['multiples'][multiple_type]
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
            'percentile_25': np.percentile(values, 25),
            'percentile_75': np.percentile(values, 75),
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
        filters: Optional[dict] = None,
        net_debt: float = 0,
        shares_outstanding: Optional[float] = None
    ) -> Dict:
        """
        Calcula valoración usando transacciones precedentes

        Args:
            target_revenue: Revenue del target
            target_ebitda: EBITDA del target
            target_ebit: EBIT del target
            target_net_income: Net Income del target
            target_book_value: Book Value del target
            statistic: Usar 'mean' o 'median'
            filters: Filtros de transacciones (max_years_old, etc.)
            net_debt: Deuda neta del target
            shares_outstanding: Acciones en circulación

        Returns:
            Diccionario con valoraciones
        """
        valuations = {}

        if target_revenue:
            stats = self.get_transaction_multiples('ev_revenue', filters)
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_revenue * multiple
                equity_value = ev - net_debt

                valuations['ev_revenue'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_revenue,
                    'transactions_count': stats['count'],
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_ebitda and target_ebitda > 0:
            stats = self.get_transaction_multiples('ev_ebitda', filters)
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_ebitda * multiple
                equity_value = ev - net_debt

                valuations['ev_ebitda'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_ebitda,
                    'transactions_count': stats['count'],
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_ebit and target_ebit > 0:
            stats = self.get_transaction_multiples('ev_ebit', filters)
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_ebit * multiple
                equity_value = ev - net_debt

                valuations['ev_ebit'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_ebit,
                    'transactions_count': stats['count'],
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_net_income and target_net_income > 0:
            stats = self.get_transaction_multiples('ev_net_income', filters)
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_net_income * multiple
                equity_value = ev - net_debt

                valuations['ev_net_income'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_net_income,
                    'transactions_count': stats['count'],
                    'multiple_range': (stats['min'], stats['max'])
                }

        if target_book_value and target_book_value > 0:
            stats = self.get_transaction_multiples('ev_book_value', filters)
            if stats['count'] > 0:
                multiple = stats[statistic]
                ev = target_book_value * multiple
                equity_value = ev - net_debt

                valuations['ev_book_value'] = {
                    'enterprise_value': ev,
                    'equity_value': equity_value,
                    'multiple_used': multiple,
                    'metric': target_book_value,
                    'transactions_count': stats['count'],
                    'multiple_range': (stats['min'], stats['max'])
                }

        # Valor por acción
        if shares_outstanding:
            for method in valuations:
                valuations[method]['value_per_share'] = \
                    valuations[method]['equity_value'] / shares_outstanding

        # Valoración promedio
        equity_values = [v['equity_value'] for v in valuations.values()]

        if equity_values:
            avg_equity = np.mean(equity_values)
            valuations['average'] = {
                'equity_value': avg_equity,
                'methods_count': len(equity_values)
            }

            if shares_outstanding:
                valuations['average']['value_per_share'] = \
                    avg_equity / shares_outstanding

        return valuations

    def get_premium_analysis(
        self,
        filters: Optional[dict] = None
    ) -> Dict:
        """
        Analiza premiums pagados en transacciones

        Args:
            filters: Filtros opcionales

        Returns:
            Estadísticas de premiums
        """
        if filters:
            transactions = self.filter_transactions(**filters)
        else:
            transactions = self.transactions

        premiums = [t['premium'] for t in transactions
                   if t['premium'] is not None]

        if not premiums:
            return {'count': 0}

        return {
            'count': len(premiums),
            'mean': np.mean(premiums),
            'median': np.median(premiums),
            'min': np.min(premiums),
            'max': np.max(premiums),
            'std': np.std(premiums),
            'percentile_25': np.percentile(premiums, 25),
            'percentile_75': np.percentile(premiums, 75)
        }

    def get_summary(self, filters: Optional[dict] = None) -> Dict:
        """
        Resumen de transacciones

        Args:
            filters: Filtros opcionales

        Returns:
            Diccionario con resumen
        """
        if filters:
            transactions = self.filter_transactions(**filters)
        else:
            transactions = self.transactions

        summary = {
            'total_transactions': len(transactions),
            'date_range': None,
            'value_range': None,
            'multiples_statistics': {}
        }

        if transactions:
            # Rango de fechas
            dates = [t['date'] for t in transactions if t['date']]
            if dates:
                summary['date_range'] = (min(dates), max(dates))

            # Rango de valores
            values = [t['transaction_value'] for t in transactions]
            summary['value_range'] = (min(values), max(values))

            # Estadísticas de múltiplos
            for mult_type in ['ev_revenue', 'ev_ebitda', 'ev_ebit']:
                stats = self.get_transaction_multiples(mult_type, filters)
                if stats['count'] > 0:
                    summary['multiples_statistics'][mult_type] = stats

            # Premium analysis
            summary['premium_statistics'] = self.get_premium_analysis(filters)

        return summary

    def __repr__(self) -> str:
        """Representación en string"""
        return (
            f"PrecedentTransactionsAnalysis(\n"
            f"  Total Transactions: {len(self.transactions)}\n"
            f"  Transactions: {[(t['acquirer_name'], t['target_name']) for t in self.transactions]}\n"
            f")"
        )
