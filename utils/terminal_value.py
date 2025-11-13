"""
Cálculo del Terminal Value para modelos DCF
"""
from typing import Literal
from .data_validation import validate_positive, validate_percentage


def calculate_terminal_value(
    final_year_fcf: float,
    wacc: float,
    method: Literal['gordon_growth', 'exit_multiple'] = 'gordon_growth',
    growth_rate: float = None,
    exit_multiple: float = None,
    final_year_ebitda: float = None
) -> float:
    """
    Calcula el Terminal Value usando el método especificado

    Args:
        final_year_fcf: Free Cash Flow del último año proyectado
        wacc: Weighted Average Cost of Capital
        method: Método de cálculo ('gordon_growth' o 'exit_multiple')
        growth_rate: Tasa de crecimiento perpetuo (para Gordon Growth)
        exit_multiple: Múltiplo de salida EV/EBITDA (para Exit Multiple)
        final_year_ebitda: EBITDA del último año (para Exit Multiple)

    Returns:
        Terminal Value

    Raises:
        ValueError: Si faltan parámetros requeridos para el método
    """
    if method == 'gordon_growth':
        if growth_rate is None:
            raise ValueError("growth_rate es requerido para método gordon_growth")

        validate_percentage(wacc, "WACC")
        validate_percentage(growth_rate, "Growth rate")

        if growth_rate >= wacc:
            raise ValueError(
                f"Growth rate ({growth_rate}) debe ser menor que WACC ({wacc})"
            )

        terminal_value = (final_year_fcf * (1 + growth_rate)) / (wacc - growth_rate)

    elif method == 'exit_multiple':
        if exit_multiple is None or final_year_ebitda is None:
            raise ValueError(
                "exit_multiple y final_year_ebitda son requeridos para método exit_multiple"
            )

        validate_positive(exit_multiple, "Exit multiple")
        validate_positive(final_year_ebitda, "Final year EBITDA")

        terminal_value = exit_multiple * final_year_ebitda

    else:
        raise ValueError(f"Método no reconocido: {method}")

    return terminal_value


class TerminalValueCalculator:
    """
    Calculadora avanzada de Terminal Value con múltiples métodos
    """

    def __init__(self, wacc: float):
        """
        Inicializa la calculadora de Terminal Value

        Args:
            wacc: Weighted Average Cost of Capital
        """
        self.wacc = validate_percentage(wacc, "WACC")

    def gordon_growth(
        self,
        final_year_fcf: float,
        perpetual_growth_rate: float
    ) -> dict:
        """
        Calcula Terminal Value usando Gordon Growth Model

        Formula: TV = FCFn * (1 + g) / (WACC - g)

        Args:
            final_year_fcf: Free Cash Flow del último año proyectado
            perpetual_growth_rate: Tasa de crecimiento perpetuo

        Returns:
            Diccionario con Terminal Value y métricas
        """
        validate_positive(final_year_fcf, "Final year FCF")
        validate_percentage(perpetual_growth_rate, "Perpetual growth rate")

        if perpetual_growth_rate >= self.wacc:
            raise ValueError(
                f"Growth rate ({perpetual_growth_rate:.2%}) debe ser menor que "
                f"WACC ({self.wacc:.2%})"
            )

        terminal_value = (final_year_fcf * (1 + perpetual_growth_rate)) / \
                        (self.wacc - perpetual_growth_rate)

        return {
            'terminal_value': terminal_value,
            'method': 'gordon_growth',
            'final_year_fcf': final_year_fcf,
            'perpetual_growth_rate': perpetual_growth_rate,
            'wacc': self.wacc,
            'implied_perpetual_fcf': final_year_fcf * (1 + perpetual_growth_rate)
        }

    def exit_multiple(
        self,
        final_year_ebitda: float,
        exit_multiple: float
    ) -> dict:
        """
        Calcula Terminal Value usando Exit Multiple Method

        Formula: TV = EBITDAn * Exit Multiple

        Args:
            final_year_ebitda: EBITDA del último año proyectado
            exit_multiple: Múltiplo de salida (EV/EBITDA)

        Returns:
            Diccionario con Terminal Value y métricas
        """
        validate_positive(final_year_ebitda, "Final year EBITDA")
        validate_positive(exit_multiple, "Exit multiple")

        terminal_value = final_year_ebitda * exit_multiple

        return {
            'terminal_value': terminal_value,
            'method': 'exit_multiple',
            'final_year_ebitda': final_year_ebitda,
            'exit_multiple': exit_multiple,
            'wacc': self.wacc
        }

    def h_model(
        self,
        final_year_fcf: float,
        initial_growth_rate: float,
        terminal_growth_rate: float,
        high_growth_years: int
    ) -> dict:
        """
        Calcula Terminal Value usando H-Model (crecimiento de dos fases)

        El H-Model asume un decrecimiento linear del growth rate desde
        initial_growth_rate hasta terminal_growth_rate

        Args:
            final_year_fcf: Free Cash Flow del último año proyectado
            initial_growth_rate: Tasa de crecimiento inicial
            terminal_growth_rate: Tasa de crecimiento terminal
            high_growth_years: Años de alto crecimiento

        Returns:
            Diccionario con Terminal Value y métricas
        """
        validate_positive(final_year_fcf, "Final year FCF")
        validate_percentage(initial_growth_rate, "Initial growth rate")
        validate_percentage(terminal_growth_rate, "Terminal growth rate")
        validate_positive(high_growth_years, "High growth years")

        if terminal_growth_rate >= self.wacc:
            raise ValueError(
                f"Terminal growth rate ({terminal_growth_rate:.2%}) debe ser menor "
                f"que WACC ({self.wacc:.2%})"
            )

        # H-Model formula
        terminal_value = final_year_fcf * (1 + terminal_growth_rate) / \
                        (self.wacc - terminal_growth_rate) * \
                        (1 + (high_growth_years / 2) * (initial_growth_rate - terminal_growth_rate))

        return {
            'terminal_value': terminal_value,
            'method': 'h_model',
            'final_year_fcf': final_year_fcf,
            'initial_growth_rate': initial_growth_rate,
            'terminal_growth_rate': terminal_growth_rate,
            'high_growth_years': high_growth_years,
            'wacc': self.wacc
        }

    def sensitivity_analysis(
        self,
        final_year_fcf: float,
        growth_rates: list,
        wacc_values: list = None
    ) -> dict:
        """
        Realiza análisis de sensibilidad del Terminal Value

        Args:
            final_year_fcf: Free Cash Flow del último año proyectado
            growth_rates: Lista de growth rates para analizar
            wacc_values: Lista opcional de WACC values (usa self.wacc si es None)

        Returns:
            Diccionario con matriz de sensibilidad
        """
        if wacc_values is None:
            wacc_values = [self.wacc]

        results = []

        for wacc in wacc_values:
            wacc_results = []
            for growth in growth_rates:
                try:
                    if growth < wacc:
                        tv = (final_year_fcf * (1 + growth)) / (wacc - growth)
                        wacc_results.append(tv)
                    else:
                        wacc_results.append(None)
                except:
                    wacc_results.append(None)

            results.append({
                'wacc': wacc,
                'terminal_values': wacc_results
            })

        return {
            'sensitivity_matrix': results,
            'growth_rates': growth_rates,
            'wacc_values': wacc_values,
            'final_year_fcf': final_year_fcf
        }
