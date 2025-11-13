"""
Análisis de Due Diligence Financiero

Herramientas para identificar red flags y analizar la calidad
de los earnings de una empresa target.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Optional, Literal
import numpy as np
from utils.data_validation import validate_positive


class DueDiligenceAnalysis:
    """
    Análisis de Due Diligence Financiero para M&A

    Identifica:
    - Red flags financieros
    - Calidad de earnings
    - Tendencias preocupantes
    - Working capital analysis
    - Normalización de EBITDA
    """

    def __init__(self):
        """Inicializa el análisis de due diligence"""
        self.periods = []
        self.red_flags = []
        self.adjustments = []

    def add_period(
        self,
        period_name: str,
        revenue: float,
        gross_profit: float,
        ebitda: float,
        net_income: float,
        operating_cash_flow: Optional[float] = None,
        accounts_receivable: Optional[float] = None,
        inventory: Optional[float] = None,
        accounts_payable: Optional[float] = None,
        deferred_revenue: Optional[float] = None,
        capex: Optional[float] = None,
        one_time_items: Optional[float] = None
    ):
        """
        Añade datos de un período para análisis

        Args:
            period_name: Nombre del período
            revenue: Ingresos
            gross_profit: Beneficio bruto
            ebitda: EBITDA
            net_income: Beneficio neto
            operating_cash_flow: Flujo de caja operativo
            accounts_receivable: Cuentas por cobrar
            inventory: Inventario
            accounts_payable: Cuentas por pagar
            deferred_revenue: Ingresos diferidos
            capex: CapEx
            one_time_items: Items extraordinarios
        """
        period = {
            'period_name': period_name,
            'revenue': validate_positive(revenue, "Revenue"),
            'gross_profit': gross_profit,
            'ebitda': ebitda,
            'net_income': net_income,
            'operating_cash_flow': operating_cash_flow,
            'accounts_receivable': accounts_receivable,
            'inventory': inventory,
            'accounts_payable': accounts_payable,
            'deferred_revenue': deferred_revenue,
            'capex': capex,
            'one_time_items': one_time_items
        }

        self.periods.append(period)

    def analyze_revenue_quality(self) -> Dict:
        """
        Analiza la calidad de los ingresos

        Returns:
            Análisis de calidad de revenue
        """
        if len(self.periods) < 2:
            return {'error': 'Se requieren al menos 2 períodos'}

        issues = []

        # 1. Revenue growth vs AR growth
        revenues = [p['revenue'] for p in self.periods]
        ars = [p['accounts_receivable'] for p in self.periods
              if p['accounts_receivable'] is not None]

        if len(ars) == len(revenues):
            revenue_growth = (revenues[-1] / revenues[0]) - 1
            ar_growth = (ars[-1] / ars[0]) - 1

            if ar_growth > revenue_growth * 1.5:
                issues.append({
                    'severity': 'high',
                    'issue': 'AR growing significantly faster than revenue',
                    'detail': f'Revenue growth: {revenue_growth:.1%}, AR growth: {ar_growth:.1%}',
                    'implication': 'Possible revenue recognition issues or deteriorating collections'
                })

        # 2. DSO (Days Sales Outstanding) trend
        dso_values = []
        for period in self.periods:
            if period['accounts_receivable'] is not None:
                dso = (period['accounts_receivable'] / period['revenue']) * 365
                dso_values.append(dso)

        if len(dso_values) >= 3:
            # Check if DSO is increasing
            dso_trend = np.polyfit(range(len(dso_values)), dso_values, 1)[0]
            if dso_trend > 5:  # Aumentando más de 5 días por período
                issues.append({
                    'severity': 'medium',
                    'issue': 'Days Sales Outstanding increasing',
                    'detail': f'DSO trend: +{dso_trend:.1f} days per period',
                    'implication': 'Collections may be slowing, potential bad debt risk'
                })

        # 3. Deferred revenue trend (si aplica)
        deferred_revs = [p['deferred_revenue'] for p in self.periods
                        if p['deferred_revenue'] is not None]

        if len(deferred_revs) >= 2:
            # Deferred revenue decreciente puede ser preocupante para SaaS
            deferred_change = (deferred_revs[-1] / deferred_revs[-2]) - 1
            if deferred_change < -0.1:  # Bajó más del 10%
                issues.append({
                    'severity': 'medium',
                    'issue': 'Deferred revenue declining',
                    'detail': f'Change: {deferred_change:.1%}',
                    'implication': 'May indicate slowing bookings or business momentum'
                })

        return {
            'issues': issues,
            'dso_trend': dso_values if dso_values else None
        }

    def analyze_earnings_quality(self) -> Dict:
        """
        Analiza la calidad de los earnings

        Returns:
            Análisis de earnings quality
        """
        if len(self.periods) < 2:
            return {'error': 'Se requieren al menos 2 períodos'}

        issues = []

        # 1. Cash Flow vs Net Income
        for i, period in enumerate(self.periods):
            if period['operating_cash_flow'] is not None:
                ocf = period['operating_cash_flow']
                ni = period['net_income']

                # OCF should generally be >= Net Income
                if ni > 0 and ocf < ni * 0.8:
                    issues.append({
                        'severity': 'high',
                        'period': period['period_name'],
                        'issue': 'Operating cash flow significantly below net income',
                        'detail': f'OCF: {ocf:,.0f}, NI: {ni:,.0f}, Ratio: {ocf/ni:.2f}',
                        'implication': 'Possible aggressive accrual accounting or working capital issues'
                    })

        # 2. Margin trends
        gross_margins = [p['gross_profit'] / p['revenue'] for p in self.periods]
        ebitda_margins = [p['ebitda'] / p['revenue'] for p in self.periods]

        if len(gross_margins) >= 3:
            # Check for declining margins
            gm_trend = np.polyfit(range(len(gross_margins)), gross_margins, 1)[0]
            if gm_trend < -0.02:  # Bajando más de 2% por período
                issues.append({
                    'severity': 'medium',
                    'issue': 'Gross margin declining',
                    'detail': f'Trend: {gm_trend:.2%} per period',
                    'implication': 'Cost pressures, pricing pressure, or mix shift'
                })

        # 3. One-time items frequency
        one_time_total = sum(p['one_time_items'] for p in self.periods
                           if p['one_time_items'] is not None)

        if one_time_total != 0:
            avg_ebitda = np.mean([p['ebitda'] for p in self.periods])
            if abs(one_time_total) > avg_ebitda * 0.2:
                issues.append({
                    'severity': 'medium',
                    'issue': 'Significant one-time items',
                    'detail': f'Total one-time items: {one_time_total:,.0f}',
                    'implication': 'Review if truly non-recurring or part of ongoing business'
                })

        return {
            'issues': issues,
            'margin_trends': {
                'gross_margins': gross_margins,
                'ebitda_margins': ebitda_margins
            }
        }

    def working_capital_analysis(self) -> Dict:
        """
        Analiza el working capital

        Returns:
            Análisis de working capital
        """
        if len(self.periods) < 2:
            return {'error': 'Se requieren al menos 2 períodos'}

        issues = []
        nwc_values = []

        for period in self.periods:
            if all(period[key] is not None for key in
                  ['accounts_receivable', 'inventory', 'accounts_payable']):

                nwc = (period['accounts_receivable'] +
                      period['inventory'] -
                      period['accounts_payable'])

                nwc_pct_revenue = nwc / period['revenue']
                nwc_values.append({
                    'period': period['period_name'],
                    'nwc': nwc,
                    'nwc_pct_revenue': nwc_pct_revenue
                })

        # Analizar tendencia de NWC
        if len(nwc_values) >= 2:
            nwc_pcts = [v['nwc_pct_revenue'] for v in nwc_values]

            # NWC creciente puede indicar problemas
            nwc_change = nwc_pcts[-1] - nwc_pcts[0]

            if nwc_change > 0.05:  # Aumentó más de 5% de revenue
                issues.append({
                    'severity': 'medium',
                    'issue': 'Working capital increasing as % of revenue',
                    'detail': f'NWC change: +{nwc_change:.1%} of revenue',
                    'implication': 'More cash tied up in operations, potential efficiency issues'
                })

            # Calcular NWC requirement para normalización
            avg_nwc_pct = np.mean(nwc_pcts)
            target_nwc = self.periods[-1]['revenue'] * avg_nwc_pct

            nwc_adjustment = target_nwc - nwc_values[-1]['nwc']

            return {
                'issues': issues,
                'nwc_history': nwc_values,
                'nwc_adjustment_required': nwc_adjustment,
                'avg_nwc_pct_revenue': avg_nwc_pct
            }

        return {'nwc_history': nwc_values}

    def normalize_ebitda(
        self,
        period_index: int = -1,
        adjustments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Normaliza el EBITDA eliminando items no recurrentes

        Args:
            period_index: Índice del período a normalizar
            adjustments: Lista de ajustes manuales
                [{'name': 'Restructuring', 'amount': 500, 'add_back': True}, ...]

        Returns:
            EBITDA normalizado
        """
        period = self.periods[period_index]
        reported_ebitda = period['ebitda']

        normalized_ebitda = reported_ebitda
        adjustment_details = []

        # One-time items registrados
        if period['one_time_items']:
            normalized_ebitda += period['one_time_items']
            adjustment_details.append({
                'item': 'One-time items',
                'amount': period['one_time_items'],
                'type': 'add_back'
            })

        # Ajustes manuales
        if adjustments:
            for adj in adjustments:
                amount = adj['amount']
                if adj.get('add_back', True):
                    normalized_ebitda += amount
                    adj_type = 'add_back'
                else:
                    normalized_ebitda -= amount
                    adj_type = 'deduct'

                adjustment_details.append({
                    'item': adj['name'],
                    'amount': amount,
                    'type': adj_type
                })

        return {
            'period': period['period_name'],
            'reported_ebitda': reported_ebitda,
            'normalized_ebitda': normalized_ebitda,
            'total_adjustments': normalized_ebitda - reported_ebitda,
            'adjustment_details': adjustment_details,
            'normalized_ebitda_margin': normalized_ebitda / period['revenue']
        }

    def get_all_red_flags(self) -> Dict:
        """
        Obtiene todos los red flags identificados

        Returns:
            Todos los red flags consolidados
        """
        all_issues = []

        # Revenue quality issues
        revenue_analysis = self.analyze_revenue_quality()
        if 'issues' in revenue_analysis:
            all_issues.extend([{**issue, 'category': 'Revenue Quality'}
                             for issue in revenue_analysis['issues']])

        # Earnings quality issues
        earnings_analysis = self.analyze_earnings_quality()
        if 'issues' in earnings_analysis:
            all_issues.extend([{**issue, 'category': 'Earnings Quality'}
                             for issue in earnings_analysis['issues']])

        # Working capital issues
        wc_analysis = self.working_capital_analysis()
        if 'issues' in wc_analysis:
            all_issues.extend([{**issue, 'category': 'Working Capital'}
                             for issue in wc_analysis['issues']])

        # Clasificar por severidad
        high_severity = [i for i in all_issues if i.get('severity') == 'high']
        medium_severity = [i for i in all_issues if i.get('severity') == 'medium']
        low_severity = [i for i in all_issues if i.get('severity') == 'low']

        return {
            'total_issues': len(all_issues),
            'high_severity': high_severity,
            'medium_severity': medium_severity,
            'low_severity': low_severity,
            'all_issues': all_issues
        }

    def generate_due_diligence_report(self) -> str:
        """
        Genera un reporte de due diligence en texto

        Returns:
            Reporte formateado
        """
        red_flags = self.get_all_red_flags()

        report = "=" * 60 + "\n"
        report += "FINANCIAL DUE DILIGENCE REPORT\n"
        report += "=" * 60 + "\n\n"

        report += f"Total Issues Identified: {red_flags['total_issues']}\n"
        report += f"  High Severity: {len(red_flags['high_severity'])}\n"
        report += f"  Medium Severity: {len(red_flags['medium_severity'])}\n"
        report += f"  Low Severity: {len(red_flags['low_severity'])}\n\n"

        if red_flags['high_severity']:
            report += "HIGH SEVERITY ISSUES:\n"
            report += "-" * 60 + "\n"
            for issue in red_flags['high_severity']:
                report += f"\n[{issue['category']}] {issue['issue']}\n"
                report += f"  Detail: {issue['detail']}\n"
                report += f"  Implication: {issue['implication']}\n"

        if red_flags['medium_severity']:
            report += "\n\nMEDIUM SEVERITY ISSUES:\n"
            report += "-" * 60 + "\n"
            for issue in red_flags['medium_severity']:
                report += f"\n[{issue['category']}] {issue['issue']}\n"
                report += f"  Detail: {issue['detail']}\n"
                report += f"  Implication: {issue['implication']}\n"

        return report

    def __repr__(self) -> str:
        """Representación en string"""
        red_flags = self.get_all_red_flags()
        return (
            f"DueDiligenceAnalysis(\n"
            f"  Periods Analyzed: {len(self.periods)}\n"
            f"  Red Flags: {red_flags['total_issues']} "
            f"(High: {len(red_flags['high_severity'])}, "
            f"Medium: {len(red_flags['medium_severity'])})\n"
            f")"
        )
