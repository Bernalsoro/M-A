"""
Modelo de Sinergias para M&A

Calcula y valora sinergias de costes e ingresos en transacciones M&A.
Incluye timeline de realización y análisis de riesgo.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Optional, Literal
import numpy as np
from utils.data_validation import validate_positive, validate_percentage, validate_non_negative


class SynergiesModel:
    """
    Modelo completo de análisis y valoración de sinergias

    Tipos de sinergias:
    1. Sinergias de Costes:
       - Reducción de headcount
       - Consolidación de instalaciones
       - Economías de escala en compras
       - Eliminación de funciones duplicadas

    2. Sinergias de Ingresos:
       - Cross-selling
       - Acceso a nuevos mercados
       - Pricing power
       - Productos complementarios
    """

    def __init__(self, wacc: float, tax_rate: float):
        """
        Inicializa el modelo de sinergias

        Args:
            wacc: Weighted Average Cost of Capital (para descontar sinergias)
            tax_rate: Tasa impositiva (para sinergias después de impuestos)
        """
        self.wacc = validate_percentage(wacc, "WACC")
        self.tax_rate = validate_percentage(tax_rate, "Tax rate")
        self.cost_synergies = []
        self.revenue_synergies = []

    def add_cost_synergy(
        self,
        name: str,
        annual_savings: float,
        implementation_cost: float,
        years_to_full_realization: int,
        realization_curve: Literal['linear', 'hockey_stick', 'immediate'] = 'linear',
        risk_adjustment: float = 1.0,
        description: str = ""
    ):
        """
        Añade una sinergia de costes

        Args:
            name: Nombre de la sinergia
            annual_savings: Ahorro anual en estado estable (run-rate)
            implementation_cost: Coste único de implementación
            years_to_full_realization: Años hasta alcanzar el run-rate completo
            realization_curve: Curva de realización de la sinergia
            risk_adjustment: Ajuste por riesgo (1.0 = sin ajuste, 0.8 = 80% probabilidad)
            description: Descripción de la sinergia
        """
        validate_positive(annual_savings, "Annual savings")
        validate_non_negative(implementation_cost, "Implementation cost")
        validate_positive(years_to_full_realization, "Years to full realization")

        synergy = {
            'type': 'cost',
            'name': name,
            'annual_savings': annual_savings,
            'implementation_cost': implementation_cost,
            'years_to_full_realization': years_to_full_realization,
            'realization_curve': realization_curve,
            'risk_adjustment': risk_adjustment,
            'description': description
        }

        # Calcular savings por año
        synergy['yearly_savings'] = self._calculate_realization_schedule(
            annual_savings,
            years_to_full_realization,
            realization_curve,
            risk_adjustment
        )

        self.cost_synergies.append(synergy)

    def add_revenue_synergy(
        self,
        name: str,
        annual_revenue_increase: float,
        cost_of_revenue_pct: float,
        implementation_cost: float,
        years_to_full_realization: int,
        realization_curve: Literal['linear', 'hockey_stick', 'immediate'] = 'linear',
        risk_adjustment: float = 0.7,  # Más conservador por defecto
        description: str = ""
    ):
        """
        Añade una sinergia de ingresos

        Args:
            name: Nombre de la sinergia
            annual_revenue_increase: Incremento anual de ingresos en estado estable
            cost_of_revenue_pct: Coste de los ingresos como % (ej: 0.6 para 60%)
            implementation_cost: Coste único de implementación
            years_to_full_realization: Años hasta alcanzar el run-rate completo
            realization_curve: Curva de realización
            risk_adjustment: Ajuste por riesgo (típicamente más bajo que cost synergies)
            description: Descripción
        """
        validate_positive(annual_revenue_increase, "Annual revenue increase")
        validate_percentage(cost_of_revenue_pct, "Cost of revenue %")
        validate_non_negative(implementation_cost, "Implementation cost")
        validate_positive(years_to_full_realization, "Years to full realization")

        # Calcular EBITDA incremental
        annual_ebitda_increase = annual_revenue_increase * (1 - cost_of_revenue_pct)

        synergy = {
            'type': 'revenue',
            'name': name,
            'annual_revenue_increase': annual_revenue_increase,
            'annual_ebitda_increase': annual_ebitda_increase,
            'cost_of_revenue_pct': cost_of_revenue_pct,
            'implementation_cost': implementation_cost,
            'years_to_full_realization': years_to_full_realization,
            'realization_curve': realization_curve,
            'risk_adjustment': risk_adjustment,
            'description': description
        }

        # Calcular EBITDA incremental por año
        synergy['yearly_ebitda'] = self._calculate_realization_schedule(
            annual_ebitda_increase,
            years_to_full_realization,
            realization_curve,
            risk_adjustment
        )

        self.revenue_synergies.append(synergy)

    def _calculate_realization_schedule(
        self,
        full_amount: float,
        years: int,
        curve: str,
        risk_adjustment: float
    ) -> List[float]:
        """
        Calcula el schedule de realización de sinergias

        Args:
            full_amount: Monto completo en estado estable
            years: Años hasta realización completa
            curve: Tipo de curva
            risk_adjustment: Ajuste por riesgo

        Returns:
            Lista de valores anuales ajustados
        """
        schedule = []

        if curve == 'immediate':
            # Realización inmediata (año 1)
            schedule = [full_amount * risk_adjustment] * years

        elif curve == 'linear':
            # Crecimiento lineal
            for year in range(1, years + 1):
                pct_realized = year / years
                schedule.append(full_amount * pct_realized * risk_adjustment)

        elif curve == 'hockey_stick':
            # Poco al principio, mucho al final
            for year in range(1, years + 1):
                if year < years - 1:
                    pct_realized = 0.2 * (year / years)
                else:
                    pct_realized = 0.2 + 0.8 * ((year - (years - 2)) / 2)
                schedule.append(full_amount * pct_realized * risk_adjustment)

        return schedule

    def calculate_synergy_value(
        self,
        projection_years: int = 10,
        terminal_growth_rate: float = 0.0
    ) -> Dict:
        """
        Calcula el valor presente de todas las sinergias

        Args:
            projection_years: Años de proyección
            terminal_growth_rate: Crecimiento perpetuo post-proyección

        Returns:
            Diccionario con valoración de sinergias
        """
        # Inicializar arrays
        cost_savings_by_year = np.zeros(projection_years)
        revenue_ebitda_by_year = np.zeros(projection_years)
        implementation_costs_by_year = np.zeros(projection_years)

        # Agregar cost synergies
        for synergy in self.cost_synergies:
            years_realized = len(synergy['yearly_savings'])

            # Añadir implementation cost en año 1
            implementation_costs_by_year[0] += synergy['implementation_cost']

            # Añadir savings
            for i, saving in enumerate(synergy['yearly_savings']):
                if i < projection_years:
                    cost_savings_by_year[i] += saving

            # Extender run-rate para años restantes
            if years_realized < projection_years:
                run_rate = synergy['yearly_savings'][-1]
                for i in range(years_realized, projection_years):
                    cost_savings_by_year[i] += run_rate

        # Agregar revenue synergies
        for synergy in self.revenue_synergies:
            years_realized = len(synergy['yearly_ebitda'])

            # Añadir implementation cost en año 1
            implementation_costs_by_year[0] += synergy['implementation_cost']

            # Añadir EBITDA incremental
            for i, ebitda in enumerate(synergy['yearly_ebitda']):
                if i < projection_years:
                    revenue_ebitda_by_year[i] += ebitda

            # Extender run-rate
            if years_realized < projection_years:
                run_rate = synergy['yearly_ebitda'][-1]
                for i in range(years_realized, projection_years):
                    revenue_ebitda_by_year[i] += run_rate

        # Calcular EBITDA total de sinergias
        total_synergy_ebitda = cost_savings_by_year + revenue_ebitda_by_year

        # Aplicar impuestos (sinergias son EBITDA, convertir a after-tax)
        # Simplificación: EBITDA * (1 - tax rate)
        after_tax_synergies = total_synergy_ebitda * (1 - self.tax_rate)

        # Restar implementation costs (después de tax shield)
        after_tax_impl_costs = implementation_costs_by_year * (1 - self.tax_rate)
        net_synergies = after_tax_synergies - after_tax_impl_costs

        # Descontar al presente
        pv_synergies = []
        for year, synergy in enumerate(net_synergies, start=1):
            pv = synergy / ((1 + self.wacc) ** year)
            pv_synergies.append(pv)

        # Calcular terminal value de sinergias
        final_year_synergy = net_synergies[-1]
        if terminal_growth_rate < self.wacc:
            terminal_value = (final_year_synergy * (1 + terminal_growth_rate)) / \
                           (self.wacc - terminal_growth_rate)
            pv_terminal_value = terminal_value / ((1 + self.wacc) ** projection_years)
        else:
            pv_terminal_value = 0

        # Totales
        total_pv_synergies = sum(pv_synergies) + pv_terminal_value

        return {
            'total_synergy_value': total_pv_synergies,
            'pv_projection_period': sum(pv_synergies),
            'pv_terminal_value': pv_terminal_value,
            'yearly_breakdown': {
                'cost_savings': cost_savings_by_year.tolist(),
                'revenue_ebitda': revenue_ebitda_by_year.tolist(),
                'implementation_costs': implementation_costs_by_year.tolist(),
                'net_after_tax_synergies': net_synergies.tolist(),
                'pv_synergies': pv_synergies
            },
            'run_rate_synergies': {
                'cost_savings': cost_savings_by_year[-1],
                'revenue_ebitda': revenue_ebitda_by_year[-1],
                'total_ebitda': total_synergy_ebitda[-1]
            }
        }

    def get_synergies_summary(self) -> Dict:
        """
        Obtiene resumen de todas las sinergias

        Returns:
            Diccionario con resumen
        """
        total_cost_savings = sum(s['annual_savings'] for s in self.cost_synergies)
        total_revenue_ebitda = sum(s['annual_ebitda_increase'] for s in self.revenue_synergies)
        total_impl_costs = sum(s['implementation_cost'] for s in self.cost_synergies + self.revenue_synergies)

        return {
            'cost_synergies': {
                'count': len(self.cost_synergies),
                'total_run_rate': total_cost_savings,
                'items': [{
                    'name': s['name'],
                    'annual_savings': s['annual_savings'],
                    'implementation_cost': s['implementation_cost'],
                    'years_to_realize': s['years_to_full_realization']
                } for s in self.cost_synergies]
            },
            'revenue_synergies': {
                'count': len(self.revenue_synergies),
                'total_run_rate_ebitda': total_revenue_ebitda,
                'items': [{
                    'name': s['name'],
                    'annual_revenue': s['annual_revenue_increase'],
                    'annual_ebitda': s['annual_ebitda_increase'],
                    'implementation_cost': s['implementation_cost'],
                    'years_to_realize': s['years_to_full_realization']
                } for s in self.revenue_synergies]
            },
            'totals': {
                'total_ebitda_run_rate': total_cost_savings + total_revenue_ebitda,
                'total_implementation_costs': total_impl_costs,
                'cost_to_achieve_ratio': total_impl_costs / (total_cost_savings + total_revenue_ebitda)
                    if (total_cost_savings + total_revenue_ebitda) > 0 else 0
            }
        }

    def synergy_risk_analysis(self) -> Dict:
        """
        Analiza el perfil de riesgo de las sinergias

        Returns:
            Análisis de riesgo
        """
        cost_risk_scores = [s['risk_adjustment'] for s in self.cost_synergies]
        revenue_risk_scores = [s['risk_adjustment'] for s in self.revenue_synergies]

        return {
            'cost_synergies_risk': {
                'average_risk_adjustment': np.mean(cost_risk_scores) if cost_risk_scores else 0,
                'min_risk_adjustment': min(cost_risk_scores) if cost_risk_scores else 0,
                'max_risk_adjustment': max(cost_risk_scores) if cost_risk_scores else 0
            },
            'revenue_synergies_risk': {
                'average_risk_adjustment': np.mean(revenue_risk_scores) if revenue_risk_scores else 0,
                'min_risk_adjustment': min(revenue_risk_scores) if revenue_risk_scores else 0,
                'max_risk_adjustment': max(revenue_risk_scores) if revenue_risk_scores else 0
            }
        }

    def __repr__(self) -> str:
        """Representación en string"""
        summary = self.get_synergies_summary()
        return (
            f"SynergiesModel(\n"
            f"  Cost Synergies: {summary['cost_synergies']['count']} "
            f"(${summary['cost_synergies']['total_run_rate']:,.0f} run-rate)\n"
            f"  Revenue Synergies: {summary['revenue_synergies']['count']} "
            f"(${summary['revenue_synergies']['total_run_rate_ebitda']:,.0f} EBITDA run-rate)\n"
            f"  Total EBITDA Run-Rate: ${summary['totals']['total_ebitda_run_rate']:,.0f}\n"
            f"  Implementation Costs: ${summary['totals']['total_implementation_costs']:,.0f}\n"
            f")"
        )
