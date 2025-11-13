"""
Cálculo del Weighted Average Cost of Capital (WACC)
"""
from typing import Optional
from .data_validation import validate_positive, validate_percentage


def calculate_wacc(
    equity_value: float,
    debt_value: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float
) -> float:
    """
    Calcula el WACC (Weighted Average Cost of Capital)

    Formula: WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)

    Donde:
    - E = Market value of equity
    - D = Market value of debt
    - V = E + D (Total value)
    - Re = Cost of equity
    - Rd = Cost of debt
    - Tc = Corporate tax rate

    Args:
        equity_value: Valor de mercado del equity
        debt_value: Valor de mercado de la deuda
        cost_of_equity: Coste del equity (en decimal, ej: 0.12 para 12%)
        cost_of_debt: Coste de la deuda (en decimal, ej: 0.05 para 5%)
        tax_rate: Tasa impositiva (en decimal, ej: 0.25 para 25%)

    Returns:
        WACC en decimal (ej: 0.10 para 10%)

    Example:
        >>> calculate_wacc(700, 300, 0.12, 0.05, 0.25)
        0.09525
    """
    # Validaciones
    validate_positive(equity_value, "Equity value")
    validate_positive(debt_value, "Debt value")
    validate_percentage(cost_of_equity, "Cost of equity")
    validate_percentage(cost_of_debt, "Cost of debt")
    validate_percentage(tax_rate, "Tax rate")

    total_value = equity_value + debt_value
    weight_equity = equity_value / total_value
    weight_debt = debt_value / total_value

    wacc = (weight_equity * cost_of_equity) + \
           (weight_debt * cost_of_debt * (1 - tax_rate))

    return wacc


class WACCCalculator:
    """
    Calculadora avanzada de WACC con diferentes metodologías
    """

    def __init__(self, tax_rate: float):
        """
        Inicializa la calculadora de WACC

        Args:
            tax_rate: Tasa impositiva corporativa (en decimal)
        """
        self.tax_rate = validate_percentage(tax_rate, "Tax rate")

    def calculate_with_capm(
        self,
        risk_free_rate: float,
        beta: float,
        market_return: float,
        debt_value: float,
        equity_value: float,
        cost_of_debt: float
    ) -> dict:
        """
        Calcula WACC usando CAPM para el coste del equity

        CAPM: Re = Rf + β * (Rm - Rf)

        Args:
            risk_free_rate: Tasa libre de riesgo
            beta: Beta del equity
            market_return: Retorno esperado del mercado
            debt_value: Valor de mercado de la deuda
            equity_value: Valor de mercado del equity
            cost_of_debt: Coste de la deuda

        Returns:
            Diccionario con WACC y componentes
        """
        # Calcular cost of equity usando CAPM
        cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)

        # Calcular WACC
        wacc = calculate_wacc(
            equity_value=equity_value,
            debt_value=debt_value,
            cost_of_equity=cost_of_equity,
            cost_of_debt=cost_of_debt,
            tax_rate=self.tax_rate
        )

        return {
            'wacc': wacc,
            'cost_of_equity': cost_of_equity,
            'cost_of_debt': cost_of_debt,
            'after_tax_cost_of_debt': cost_of_debt * (1 - self.tax_rate),
            'weight_equity': equity_value / (equity_value + debt_value),
            'weight_debt': debt_value / (equity_value + debt_value)
        }

    def calculate_with_debt_schedule(
        self,
        equity_value: float,
        debt_tranches: list,
        cost_of_equity: float
    ) -> dict:
        """
        Calcula WACC con múltiples tranches de deuda

        Args:
            equity_value: Valor de mercado del equity
            debt_tranches: Lista de diccionarios con 'amount' y 'rate' para cada tranche
            cost_of_equity: Coste del equity

        Returns:
            Diccionario con WACC y componentes

        Example:
            >>> calc = WACCCalculator(tax_rate=0.25)
            >>> calc.calculate_with_debt_schedule(
            ...     equity_value=700,
            ...     debt_tranches=[
            ...         {'amount': 200, 'rate': 0.04},
            ...         {'amount': 100, 'rate': 0.06}
            ...     ],
            ...     cost_of_equity=0.12
            ... )
        """
        # Calcular weighted average cost of debt
        total_debt = sum(tranche['amount'] for tranche in debt_tranches)
        weighted_cost_of_debt = sum(
            tranche['amount'] * tranche['rate'] for tranche in debt_tranches
        ) / total_debt if total_debt > 0 else 0

        # Calcular WACC
        wacc = calculate_wacc(
            equity_value=equity_value,
            debt_value=total_debt,
            cost_of_equity=cost_of_equity,
            cost_of_debt=weighted_cost_of_debt,
            tax_rate=self.tax_rate
        )

        return {
            'wacc': wacc,
            'cost_of_equity': cost_of_equity,
            'weighted_cost_of_debt': weighted_cost_of_debt,
            'after_tax_cost_of_debt': weighted_cost_of_debt * (1 - self.tax_rate),
            'total_debt': total_debt,
            'weight_equity': equity_value / (equity_value + total_debt),
            'weight_debt': total_debt / (equity_value + total_debt),
            'debt_tranches': debt_tranches
        }

    def calculate_unlevered_beta(
        self,
        levered_beta: float,
        debt_to_equity: float
    ) -> float:
        """
        Calcula el beta unlevered (sin apalancamiento)

        Formula: βu = βl / [1 + (1 - Tc) * (D/E)]

        Args:
            levered_beta: Beta con apalancamiento
            debt_to_equity: Ratio Deuda/Equity

        Returns:
            Beta unlevered
        """
        unlevered_beta = levered_beta / (1 + (1 - self.tax_rate) * debt_to_equity)
        return unlevered_beta

    def calculate_levered_beta(
        self,
        unlevered_beta: float,
        debt_to_equity: float
    ) -> float:
        """
        Calcula el beta levered (con apalancamiento)

        Formula: βl = βu * [1 + (1 - Tc) * (D/E)]

        Args:
            unlevered_beta: Beta sin apalancamiento
            debt_to_equity: Ratio Deuda/Equity

        Returns:
            Beta levered
        """
        levered_beta = unlevered_beta * (1 + (1 - self.tax_rate) * debt_to_equity)
        return levered_beta
