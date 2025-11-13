"""
Modelo DCF (Discounted Cash Flow) para valoración de empresas
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Optional, Dict, Union
import numpy as np
from utils.wacc import calculate_wacc
from utils.terminal_value import TerminalValueCalculator
from utils.data_validation import validate_positive, validate_percentage, validate_list


class DCFModel:
    """
    Modelo completo de Discounted Cash Flow (DCF)

    El modelo DCF valora una empresa basándose en el valor presente
    de sus flujos de caja futuros proyectados.

    Componentes principales:
    1. Free Cash Flows proyectados
    2. WACC (Weighted Average Cost of Capital)
    3. Terminal Value
    4. Ajustes (Net Debt, Minority Interest, etc.)
    """

    def __init__(
        self,
        free_cash_flows: List[float],
        wacc: float,
        terminal_growth_rate: Optional[float] = None,
        exit_multiple: Optional[float] = None,
        final_year_ebitda: Optional[float] = None,
        net_debt: float = 0,
        minority_interest: float = 0,
        non_operating_assets: float = 0,
        shares_outstanding: Optional[float] = None
    ):
        """
        Inicializa el modelo DCF

        Args:
            free_cash_flows: Lista de FCF proyectados (excluye año 0/actual)
            wacc: Weighted Average Cost of Capital (en decimal, ej: 0.10 para 10%)
            terminal_growth_rate: Tasa de crecimiento perpetuo (Gordon Growth)
            exit_multiple: Múltiplo de salida EV/EBITDA (Exit Multiple method)
            final_year_ebitda: EBITDA del último año (para Exit Multiple)
            net_debt: Deuda neta (Debt - Cash)
            minority_interest: Intereses minoritarios
            non_operating_assets: Activos no operativos
            shares_outstanding: Acciones en circulación (para valor por acción)

        Example:
            >>> dcf = DCFModel(
            ...     free_cash_flows=[100, 110, 121, 133, 146],
            ...     wacc=0.10,
            ...     terminal_growth_rate=0.03,
            ...     net_debt=200,
            ...     shares_outstanding=1000
            ... )
        """
        # Validaciones
        self.free_cash_flows = validate_list(free_cash_flows, min_length=1, name="Free Cash Flows")
        self.wacc = validate_percentage(wacc, "WACC")
        self.net_debt = net_debt  # Puede ser negativo (net cash)
        self.minority_interest = minority_interest
        self.non_operating_assets = non_operating_assets
        self.shares_outstanding = shares_outstanding

        # Terminal Value method
        if terminal_growth_rate is not None:
            self.terminal_method = 'gordon_growth'
            self.terminal_growth_rate = validate_percentage(
                terminal_growth_rate, "Terminal growth rate"
            )
            self.exit_multiple = None
            self.final_year_ebitda = None
        elif exit_multiple is not None and final_year_ebitda is not None:
            self.terminal_method = 'exit_multiple'
            self.exit_multiple = validate_positive(exit_multiple, "Exit multiple")
            self.final_year_ebitda = validate_positive(
                final_year_ebitda, "Final year EBITDA"
            )
            self.terminal_growth_rate = None
        else:
            raise ValueError(
                "Debe proporcionar terminal_growth_rate O (exit_multiple + final_year_ebitda)"
            )

        self.projection_years = len(free_cash_flows)

    def calculate_pv_fcf(self) -> Dict[str, Union[List[float], float]]:
        """
        Calcula el valor presente de los Free Cash Flows

        Returns:
            Diccionario con FCFs descontados y suma total
        """
        pv_fcfs = []
        for year, fcf in enumerate(self.free_cash_flows, start=1):
            discount_factor = (1 + self.wacc) ** year
            pv_fcf = fcf / discount_factor
            pv_fcfs.append(pv_fcf)

        return {
            'pv_fcfs': pv_fcfs,
            'total_pv_fcf': sum(pv_fcfs),
            'discount_factors': [(1 + self.wacc) ** -year
                               for year in range(1, self.projection_years + 1)]
        }

    def calculate_terminal_value(self) -> Dict[str, float]:
        """
        Calcula el Terminal Value y su valor presente

        Returns:
            Diccionario con Terminal Value y PV Terminal Value
        """
        tv_calc = TerminalValueCalculator(wacc=self.wacc)
        final_year_fcf = self.free_cash_flows[-1]

        if self.terminal_method == 'gordon_growth':
            result = tv_calc.gordon_growth(
                final_year_fcf=final_year_fcf,
                perpetual_growth_rate=self.terminal_growth_rate
            )
        else:  # exit_multiple
            result = tv_calc.exit_multiple(
                final_year_ebitda=self.final_year_ebitda,
                exit_multiple=self.exit_multiple
            )

        terminal_value = result['terminal_value']

        # Descontar Terminal Value al presente
        discount_factor = (1 + self.wacc) ** self.projection_years
        pv_terminal_value = terminal_value / discount_factor

        return {
            'terminal_value': terminal_value,
            'pv_terminal_value': pv_terminal_value,
            'discount_factor': 1 / discount_factor,
            'method': self.terminal_method
        }

    def calculate_enterprise_value(self) -> Dict[str, float]:
        """
        Calcula el Enterprise Value

        EV = PV(FCFs) + PV(Terminal Value)

        Returns:
            Diccionario con componentes del Enterprise Value
        """
        pv_fcf_result = self.calculate_pv_fcf()
        tv_result = self.calculate_terminal_value()

        enterprise_value = pv_fcf_result['total_pv_fcf'] + tv_result['pv_terminal_value']

        return {
            'enterprise_value': enterprise_value,
            'pv_fcf': pv_fcf_result['total_pv_fcf'],
            'pv_terminal_value': tv_result['pv_terminal_value'],
            'terminal_value_percentage': tv_result['pv_terminal_value'] / enterprise_value
        }

    def calculate_equity_value(self) -> Dict[str, float]:
        """
        Calcula el Equity Value

        Equity Value = EV - Net Debt - Minority Interest + Non-Operating Assets

        Returns:
            Diccionario con Equity Value y valor por acción
        """
        ev_result = self.calculate_enterprise_value()
        enterprise_value = ev_result['enterprise_value']

        equity_value = (
            enterprise_value
            - self.net_debt
            - self.minority_interest
            + self.non_operating_assets
        )

        result = {
            'equity_value': equity_value,
            'enterprise_value': enterprise_value,
            'net_debt': self.net_debt,
            'minority_interest': self.minority_interest,
            'non_operating_assets': self.non_operating_assets
        }

        if self.shares_outstanding:
            result['value_per_share'] = equity_value / self.shares_outstanding
            result['shares_outstanding'] = self.shares_outstanding

        return result

    def calculate_valuation(self) -> Dict:
        """
        Calcula la valoración completa

        Returns:
            Diccionario completo con todos los componentes de la valoración
        """
        pv_fcf = self.calculate_pv_fcf()
        terminal_value = self.calculate_terminal_value()
        ev = self.calculate_enterprise_value()
        equity = self.calculate_equity_value()

        return {
            'equity_value': equity['equity_value'],
            'enterprise_value': ev['enterprise_value'],
            'value_per_share': equity.get('value_per_share'),
            'pv_fcf': pv_fcf['total_pv_fcf'],
            'pv_terminal_value': terminal_value['pv_terminal_value'],
            'terminal_value': terminal_value['terminal_value'],
            'net_debt': self.net_debt,
            'wacc': self.wacc,
            'projection_years': self.projection_years,
            'terminal_method': self.terminal_method,
            'fcf_breakdown': {
                'fcfs': self.free_cash_flows,
                'pv_fcfs': pv_fcf['pv_fcfs'],
                'discount_factors': pv_fcf['discount_factors']
            }
        }

    def sensitivity_analysis(
        self,
        wacc_range: tuple = (-0.02, 0.02, 0.005),
        terminal_growth_range: tuple = (-0.01, 0.01, 0.005)
    ) -> Dict:
        """
        Realiza análisis de sensibilidad del valor

        Args:
            wacc_range: Tuple (min_delta, max_delta, step) para WACC
            terminal_growth_range: Tuple (min_delta, max_delta, step) para terminal growth

        Returns:
            Diccionario con matriz de sensibilidad

        Example:
            >>> analysis = dcf.sensitivity_analysis(
            ...     wacc_range=(-0.02, 0.02, 0.005),
            ...     terminal_growth_range=(-0.01, 0.01, 0.005)
            ... )
        """
        wacc_values = np.arange(
            self.wacc + wacc_range[0],
            self.wacc + wacc_range[1] + wacc_range[2],
            wacc_range[2]
        )

        if self.terminal_method == 'gordon_growth':
            growth_values = np.arange(
                self.terminal_growth_rate + terminal_growth_range[0],
                self.terminal_growth_rate + terminal_growth_range[1] + terminal_growth_range[2],
                terminal_growth_range[2]
            )

            sensitivity_matrix = []

            for wacc in wacc_values:
                row = []
                for growth in growth_values:
                    try:
                        # Crear DCF temporal con nuevos parámetros
                        temp_dcf = DCFModel(
                            free_cash_flows=self.free_cash_flows,
                            wacc=wacc,
                            terminal_growth_rate=growth,
                            net_debt=self.net_debt,
                            minority_interest=self.minority_interest,
                            non_operating_assets=self.non_operating_assets,
                            shares_outstanding=self.shares_outstanding
                        )
                        result = temp_dcf.calculate_equity_value()
                        value = result.get('value_per_share', result['equity_value'])
                        row.append(value)
                    except:
                        row.append(None)
                sensitivity_matrix.append(row)

            return {
                'sensitivity_matrix': sensitivity_matrix,
                'wacc_values': wacc_values.tolist(),
                'terminal_growth_values': growth_values.tolist(),
                'base_case_value': self.calculate_equity_value().get(
                    'value_per_share',
                    self.calculate_equity_value()['equity_value']
                )
            }
        else:
            # Para exit multiple, variar el múltiplo en lugar de growth rate
            multiple_range = (-2, 2, 0.5)
            multiple_values = np.arange(
                self.exit_multiple + multiple_range[0],
                self.exit_multiple + multiple_range[1] + multiple_range[2],
                multiple_range[2]
            )

            sensitivity_matrix = []

            for wacc in wacc_values:
                row = []
                for multiple in multiple_values:
                    try:
                        temp_dcf = DCFModel(
                            free_cash_flows=self.free_cash_flows,
                            wacc=wacc,
                            exit_multiple=multiple,
                            final_year_ebitda=self.final_year_ebitda,
                            net_debt=self.net_debt,
                            minority_interest=self.minority_interest,
                            non_operating_assets=self.non_operating_assets,
                            shares_outstanding=self.shares_outstanding
                        )
                        result = temp_dcf.calculate_equity_value()
                        value = result.get('value_per_share', result['equity_value'])
                        row.append(value)
                    except:
                        row.append(None)
                sensitivity_matrix.append(row)

            return {
                'sensitivity_matrix': sensitivity_matrix,
                'wacc_values': wacc_values.tolist(),
                'exit_multiple_values': multiple_values.tolist(),
                'base_case_value': self.calculate_equity_value().get(
                    'value_per_share',
                    self.calculate_equity_value()['equity_value']
                )
            }

    def __repr__(self) -> str:
        """Representación en string del modelo"""
        valuation = self.calculate_valuation()
        return (
            f"DCFModel(\n"
            f"  Enterprise Value: ${valuation['enterprise_value']:,.0f}\n"
            f"  Equity Value: ${valuation['equity_value']:,.0f}\n"
            f"  Value per Share: ${valuation.get('value_per_share', 'N/A')}\n"
            f"  WACC: {self.wacc:.2%}\n"
            f"  Projection Years: {self.projection_years}\n"
            f")"
        )
