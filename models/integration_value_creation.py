"""
Modelo de Integración y Creación de Valor Post-Merger

Tracking de value creation post-merger:
- Realización de sinergias
- KPIs de integración
- Value creation waterfall
- TSR (Total Shareholder Return) analysis
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Optional, Literal
from datetime import datetime, timedelta
import numpy as np
from utils.data_validation import validate_positive, validate_percentage


class IntegrationValueCreation:
    """
    Modelo de tracking de integración y creación de valor post-merger

    Rastrea:
    - Realización de sinergias vs targets
    - KPIs operativos de integración
    - Value creation breakdown
    - Performance vs plan
    """

    def __init__(
        self,
        deal_close_date: str,
        purchase_price: float,
        synergy_targets: Dict[str, float],
        integration_costs: float
    ):
        """
        Inicializa el tracking de integración

        Args:
            deal_close_date: Fecha de cierre (YYYY-MM-DD)
            purchase_price: Precio pagado por la adquisición
            synergy_targets: Dict con targets de sinergias
                {'cost_synergies': X, 'revenue_synergies': Y}
            integration_costs: Costes totales de integración estimados
        """
        self.deal_close_date = datetime.strptime(deal_close_date, '%Y-%m-%d')
        self.purchase_price = validate_positive(purchase_price, "Purchase price")
        self.synergy_targets = synergy_targets
        self.integration_costs = integration_costs

        self.synergy_updates = []
        self.kpi_updates = []
        self.milestones = []

    def add_synergy_update(
        self,
        update_date: str,
        realized_cost_synergies: float,
        realized_revenue_synergies: float,
        run_rate_cost_synergies: float,
        run_rate_revenue_synergies: float,
        integration_costs_incurred: float
    ):
        """
        Añade actualización del estado de sinergias

        Args:
            update_date: Fecha del update (YYYY-MM-DD)
            realized_cost_synergies: Sinergias de coste realizadas (actual P&L impact)
            realized_revenue_synergies: Sinergias de revenue realizadas
            run_rate_cost_synergies: Run-rate actual de cost synergies
            run_rate_revenue_synergies: Run-rate actual de revenue synergies
            integration_costs_incurred: Costes de integración incurridos hasta la fecha
        """
        update = {
            'date': datetime.strptime(update_date, '%Y-%m-%d'),
            'months_since_close': (datetime.strptime(update_date, '%Y-%m-%d') -
                                  self.deal_close_date).days / 30.44,
            'realized_cost_synergies': realized_cost_synergies,
            'realized_revenue_synergies': realized_revenue_synergies,
            'run_rate_cost_synergies': run_rate_cost_synergies,
            'run_rate_revenue_synergies': run_rate_revenue_synergies,
            'integration_costs_incurred': integration_costs_incurred
        }

        # Calcular % de achievement vs targets
        if 'cost_synergies' in self.synergy_targets:
            update['cost_synergies_achievement'] = \
                run_rate_cost_synergies / self.synergy_targets['cost_synergies']

        if 'revenue_synergies' in self.synergy_targets:
            update['revenue_synergies_achievement'] = \
                run_rate_revenue_synergies / self.synergy_targets['revenue_synergies']

        self.synergy_updates.append(update)

    def add_kpi_update(
        self,
        update_date: str,
        kpis: Dict[str, float]
    ):
        """
        Añade actualización de KPIs operativos

        Args:
            update_date: Fecha del update
            kpis: Diccionario con KPIs
                Ejemplos: {
                    'employee_retention': 0.92,
                    'customer_retention': 0.95,
                    'revenue_run_rate': 100000000,
                    'ebitda_margin': 0.25,
                    'integration_milestones_complete': 0.75
                }
        """
        update = {
            'date': datetime.strptime(update_date, '%Y-%m-%d'),
            'months_since_close': (datetime.strptime(update_date, '%Y-%m-%d') -
                                  self.deal_close_date).days / 30.44,
            'kpis': kpis
        }

        self.kpi_updates.append(update)

    def add_integration_milestone(
        self,
        milestone_name: str,
        target_date: str,
        actual_date: Optional[str] = None,
        status: Literal['completed', 'in_progress', 'delayed', 'not_started'] = 'not_started',
        impact: Literal['high', 'medium', 'low'] = 'medium'
    ):
        """
        Añade milestone de integración

        Args:
            milestone_name: Nombre del milestone
            target_date: Fecha objetivo
            actual_date: Fecha real de completación (si completed)
            status: Estado del milestone
            impact: Impacto del milestone
        """
        milestone = {
            'name': milestone_name,
            'target_date': datetime.strptime(target_date, '%Y-%m-%d'),
            'actual_date': datetime.strptime(actual_date, '%Y-%m-%d') if actual_date else None,
            'status': status,
            'impact': impact
        }

        # Calcular delay si está completed
        if actual_date and status == 'completed':
            delay_days = (milestone['actual_date'] - milestone['target_date']).days
            milestone['delay_days'] = delay_days
            milestone['on_time'] = delay_days <= 0

        self.milestones.append(milestone)

    def calculate_synergy_realization_rate(self) -> Dict:
        """
        Calcula la tasa de realización de sinergias

        Returns:
            Análisis de realización de sinergias
        """
        if not self.synergy_updates:
            return {'error': 'No synergy updates available'}

        latest_update = self.synergy_updates[-1]

        # Cost synergies
        cost_synergy_target = self.synergy_targets.get('cost_synergies', 0)
        cost_run_rate = latest_update['run_rate_cost_synergies']
        cost_realized = latest_update['realized_cost_synergies']

        # Revenue synergies
        revenue_synergy_target = self.synergy_targets.get('revenue_synergies', 0)
        revenue_run_rate = latest_update['run_rate_revenue_synergies']
        revenue_realized = latest_update['realized_revenue_synergies']

        return {
            'as_of_date': latest_update['date'].strftime('%Y-%m-%d'),
            'months_since_close': latest_update['months_since_close'],
            'cost_synergies': {
                'target': cost_synergy_target,
                'run_rate_achieved': cost_run_rate,
                'pct_of_target': cost_run_rate / cost_synergy_target if cost_synergy_target > 0 else 0,
                'realized_to_date': cost_realized
            },
            'revenue_synergies': {
                'target': revenue_synergy_target,
                'run_rate_achieved': revenue_run_rate,
                'pct_of_target': revenue_run_rate / revenue_synergy_target if revenue_synergy_target > 0 else 0,
                'realized_to_date': revenue_realized
            },
            'total_synergies': {
                'target': cost_synergy_target + revenue_synergy_target,
                'run_rate_achieved': cost_run_rate + revenue_run_rate,
                'realized_to_date': cost_realized + revenue_realized
            },
            'integration_costs': {
                'budget': self.integration_costs,
                'incurred': latest_update['integration_costs_incurred'],
                'pct_of_budget': latest_update['integration_costs_incurred'] / self.integration_costs
                    if self.integration_costs > 0 else 0
            }
        }

    def value_creation_waterfall(self, current_market_value: float) -> Dict:
        """
        Crea value creation waterfall

        Args:
            current_market_value: Valor de mercado actual de la entidad combinada

        Returns:
            Waterfall de creación de valor
        """
        if not self.synergy_updates:
            return {'error': 'No synergy updates available'}

        latest_update = self.synergy_updates[-1]

        # Componentes del waterfall
        purchase_price = self.purchase_price
        realized_synergies = (latest_update['realized_cost_synergies'] +
                            latest_update['realized_revenue_synergies'])
        integration_costs = latest_update['integration_costs_incurred']

        # Value creation (simplificado)
        net_synergies = realized_synergies - integration_costs
        other_value_creation = current_market_value - purchase_price - net_synergies

        return {
            'purchase_price': purchase_price,
            'realized_synergies': realized_synergies,
            'integration_costs': -integration_costs,  # Negativo
            'net_synergies': net_synergies,
            'other_value_creation': other_value_creation,
            'current_market_value': current_market_value,
            'total_value_created': current_market_value - purchase_price,
            'value_created_pct': (current_market_value / purchase_price - 1) if purchase_price > 0 else 0
        }

    def integration_scorecard(self) -> Dict:
        """
        Genera scorecard de integración

        Returns:
            Scorecard con métricas clave
        """
        scorecard = {}

        # Synergy realization
        if self.synergy_updates:
            synergy_status = self.calculate_synergy_realization_rate()
            total_achieved = synergy_status['total_synergies']['pct_of_target']

            scorecard['synergy_realization'] = {
                'score': min(total_achieved * 100, 100),
                'status': 'On Track' if total_achieved >= 0.9 else
                         'At Risk' if total_achieved >= 0.7 else 'Behind',
                'details': synergy_status
            }

        # Integration milestones
        if self.milestones:
            completed = [m for m in self.milestones if m['status'] == 'completed']
            on_time = [m for m in completed if m.get('on_time', False)]

            scorecard['milestones'] = {
                'score': (len(on_time) / len(self.milestones)) * 100 if self.milestones else 0,
                'total': len(self.milestones),
                'completed': len(completed),
                'on_time': len(on_time),
                'completion_rate': len(completed) / len(self.milestones) if self.milestones else 0
            }

        # KPI performance
        if self.kpi_updates:
            latest_kpis = self.kpi_updates[-1]['kpis']

            # Calcular score basado en KPIs críticos
            kpi_scores = []

            if 'employee_retention' in latest_kpis:
                # Target: >90%
                retention = latest_kpis['employee_retention']
                score = min(retention / 0.90 * 100, 100)
                kpi_scores.append(score)

            if 'customer_retention' in latest_kpis:
                # Target: >95%
                retention = latest_kpis['customer_retention']
                score = min(retention / 0.95 * 100, 100)
                kpi_scores.append(score)

            scorecard['kpi_performance'] = {
                'score': np.mean(kpi_scores) if kpi_scores else 0,
                'latest_kpis': latest_kpis
            }

        # Overall score
        scores = [v['score'] for v in scorecard.values() if 'score' in v]
        scorecard['overall_score'] = np.mean(scores) if scores else 0

        if scorecard['overall_score'] >= 85:
            scorecard['overall_status'] = 'Excellent'
        elif scorecard['overall_score'] >= 70:
            scorecard['overall_status'] = 'Good'
        elif scorecard['overall_score'] >= 50:
            scorecard['overall_status'] = 'At Risk'
        else:
            scorecard['overall_status'] = 'Critical'

        return scorecard

    def generate_integration_report(self) -> str:
        """
        Genera reporte de integración

        Returns:
            Reporte formateado
        """
        scorecard = self.integration_scorecard()

        report = "=" * 70 + "\n"
        report += "POST-MERGER INTEGRATION REPORT\n"
        report += "=" * 70 + "\n\n"

        if self.synergy_updates:
            latest = self.synergy_updates[-1]
            report += f"As of: {latest['date'].strftime('%Y-%m-%d')} "
            report += f"(Month {latest['months_since_close']:.1f} post-close)\n\n"

        report += f"OVERALL STATUS: {scorecard.get('overall_status', 'N/A')}\n"
        report += f"Overall Score: {scorecard.get('overall_score', 0):.1f}/100\n\n"

        # Synergies
        if 'synergy_realization' in scorecard:
            syn = scorecard['synergy_realization']['details']
            report += "SYNERGY REALIZATION:\n"
            report += "-" * 70 + "\n"
            report += f"Status: {scorecard['synergy_realization']['status']}\n"
            report += f"Total Synergies Target: ${syn['total_synergies']['target']:,.0f}\n"
            report += f"Run-Rate Achieved: ${syn['total_synergies']['run_rate_achieved']:,.0f} "
            report += f"({syn['total_synergies']['pct_of_target']:.1%})\n"
            report += f"Realized to Date: ${syn['total_synergies']['realized_to_date']:,.0f}\n\n"

        # Milestones
        if 'milestones' in scorecard:
            m = scorecard['milestones']
            report += "INTEGRATION MILESTONES:\n"
            report += "-" * 70 + "\n"
            report += f"Completed: {m['completed']}/{m['total']} ({m['completion_rate']:.1%})\n"
            report += f"On-Time Completion: {m['on_time']}/{m['completed']}\n\n"

        # KPIs
        if 'kpi_performance' in scorecard:
            report += "KEY PERFORMANCE INDICATORS:\n"
            report += "-" * 70 + "\n"
            for kpi, value in scorecard['kpi_performance']['latest_kpis'].items():
                if isinstance(value, float):
                    if value < 1:
                        report += f"{kpi}: {value:.1%}\n"
                    else:
                        report += f"{kpi}: {value:,.0f}\n"

        return report

    def __repr__(self) -> str:
        """Representación en string"""
        scorecard = self.integration_scorecard()
        return (
            f"IntegrationValueCreation(\n"
            f"  Deal Close: {self.deal_close_date.strftime('%Y-%m-%d')}\n"
            f"  Purchase Price: ${self.purchase_price:,.0f}\n"
            f"  Overall Status: {scorecard.get('overall_status', 'N/A')}\n"
            f"  Overall Score: {scorecard.get('overall_score', 0):.1f}/100\n"
            f"  Updates: {len(self.synergy_updates)} synergy, {len(self.kpi_updates)} KPI\n"
            f")"
        )
