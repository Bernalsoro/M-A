"""
Modelo LBO (Leveraged Buyout)

Análisis completo de LBO incluyendo:
- Estructura de capital
- Cascada de pagos de deuda
- Cálculo de returns (IRR, MOIC)
- Análisis de sensibilidad
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Optional
import numpy as np
from scipy.optimize import newton
from utils.data_validation import validate_positive, validate_percentage, validate_non_negative


class LBOModel:
    """
    Modelo completo de Leveraged Buyout (LBO)

    El modelo LBO analiza la compra de una empresa usando apalancamiento
    significativo y calcula los retornos para los inversores de equity.
    """

    def __init__(
        self,
        purchase_price: float,
        purchase_ebitda: float,
        equity_investment: float,
        debt_amount: float,
        interest_rate: float,
        holding_period: int,
        exit_multiple: float,
        tax_rate: float = 0.25
    ):
        """
        Inicializa el modelo LBO

        Args:
            purchase_price: Precio de compra (Enterprise Value)
            purchase_ebitda: EBITDA en el año de compra
            equity_investment: Inversión de equity
            debt_amount: Deuda total al inicio
            interest_rate: Tasa de interés de la deuda
            holding_period: Período de tenencia (años)
            exit_multiple: Múltiplo de salida (EV/EBITDA)
            tax_rate: Tasa impositiva
        """
        self.purchase_price = validate_positive(purchase_price, "Purchase price")
        self.purchase_ebitda = validate_positive(purchase_ebitda, "Purchase EBITDA")
        self.equity_investment = validate_positive(equity_investment, "Equity investment")
        self.debt_amount = validate_positive(debt_amount, "Debt amount")
        self.interest_rate = validate_percentage(interest_rate, "Interest rate")
        self.holding_period = validate_positive(holding_period, "Holding period")
        self.exit_multiple = validate_positive(exit_multiple, "Exit multiple")
        self.tax_rate = validate_percentage(tax_rate, "Tax rate")

        # Validar que equity + debt = purchase price (aproximadamente)
        sources_and_uses = self.equity_investment + self.debt_amount
        if abs(sources_and_uses - purchase_price) > purchase_price * 0.01:  # 1% tolerance
            raise ValueError(
                f"Equity ({equity_investment}) + Debt ({debt_amount}) debe aproximadamente "
                f"igualar Purchase Price ({purchase_price})"
            )

        self.purchase_multiple = purchase_price / purchase_ebitda

        # Proyecciones a completar
        self.ebitda_projections = []
        self.capex_projections = []
        self.nwc_changes = []
        self.debt_schedule = []

    def project_financials(
        self,
        ebitda_growth_rates: List[float],
        capex_pct_of_revenue: List[float],
        revenue_growth_rates: List[float],
        nwc_pct_of_revenue: float = 0.15,
        depreciation_pct_of_revenue: List[float] = None
    ):
        """
        Proyecta los financials del LBO

        Args:
            ebitda_growth_rates: Growth rates de EBITDA por año
            capex_pct_of_revenue: CapEx como % de revenue por año
            revenue_growth_rates: Growth rates de revenue por año
            nwc_pct_of_revenue: Net Working Capital como % de revenue
            depreciation_pct_of_revenue: D&A como % de revenue (opcional)
        """
        if len(ebitda_growth_rates) != self.holding_period:
            raise ValueError(
                f"ebitda_growth_rates debe tener {self.holding_period} elementos"
            )

        if len(revenue_growth_rates) != self.holding_period:
            raise ValueError(
                f"revenue_growth_rates debe tener {self.holding_period} elementos"
            )

        # Proyectar EBITDA
        self.ebitda_projections = [self.purchase_ebitda]
        for growth in ebitda_growth_rates:
            next_ebitda = self.ebitda_projections[-1] * (1 + growth)
            self.ebitda_projections.append(next_ebitda)

        # Proyectar revenue (necesario para CapEx y NWC)
        # Asumir revenue basado en EBITDA margin (simplificación)
        # O usar growth rates directos
        revenue = self.purchase_price  # Simplificación inicial
        revenues = [revenue]

        for growth in revenue_growth_rates:
            revenue = revenue * (1 + growth)
            revenues.append(revenue)

        # Proyectar CapEx
        self.capex_projections = []
        for i, pct in enumerate(capex_pct_of_revenue):
            capex = revenues[i + 1] * pct  # i+1 porque revenues incluye año 0
            self.capex_projections.append(capex)

        # Proyectar cambios en NWC
        self.nwc_changes = []
        prev_nwc = revenues[0] * nwc_pct_of_revenue

        for i in range(1, len(revenues)):
            current_nwc = revenues[i] * nwc_pct_of_revenue
            nwc_change = current_nwc - prev_nwc
            self.nwc_changes.append(nwc_change)
            prev_nwc = current_nwc

        # Proyectar D&A (simplificación: usar % de revenue o asumir constante)
        if depreciation_pct_of_revenue:
            self.depreciation = [revenues[i + 1] * pct
                                for i, pct in enumerate(depreciation_pct_of_revenue)]
        else:
            # Asumir D&A constante como % de CapEx
            self.depreciation = [capex * 0.8 for capex in self.capex_projections]

    def calculate_debt_paydown(
        self,
        mandatory_paydown_pct: float = 0.5,
        cash_sweep_pct: float = 0.75
    ):
        """
        Calcula el schedule de pago de deuda

        Args:
            mandatory_paydown_pct: % de FCF destinado a pago obligatorio de deuda
            cash_sweep_pct: % de excess cash destinado a pago de deuda
        """
        if not self.ebitda_projections or not self.capex_projections:
            raise ValueError("Debe ejecutar project_financials() primero")

        debt_balance = self.debt_amount
        self.debt_schedule = [debt_balance]

        for i in range(self.holding_period):
            ebitda = self.ebitda_projections[i + 1]  # i+1 porque proyections incluye año 0
            depreciation = self.depreciation[i]
            capex = self.capex_projections[i]
            nwc_change = self.nwc_changes[i]

            # Calcular EBIT
            ebit = ebitda - depreciation

            # Calcular taxes
            interest_expense = debt_balance * self.interest_rate
            ebt = ebit - interest_expense
            taxes = max(0, ebt * self.tax_rate)

            # Calcular Free Cash Flow
            fcf = ebit - taxes - capex - nwc_change + depreciation

            # Pago de deuda
            cash_available_for_debt = fcf - interest_expense
            debt_paydown = max(0, cash_available_for_debt * cash_sweep_pct)

            # Actualizar balance de deuda
            debt_balance = max(0, debt_balance - debt_paydown)
            self.debt_schedule.append(debt_balance)

    def calculate_returns(self) -> Dict:
        """
        Calcula IRR y MOIC del LBO

        Returns:
            Diccionario con métricas de retorno
        """
        if not self.debt_schedule:
            raise ValueError("Debe ejecutar calculate_debt_paydown() primero")

        # Exit EBITDA
        exit_ebitda = self.ebitda_projections[-1]

        # Exit Enterprise Value
        exit_ev = exit_ebitda * self.exit_multiple

        # Exit Equity Value
        exit_debt = self.debt_schedule[-1]
        exit_equity_value = exit_ev - exit_debt

        # MOIC (Multiple on Invested Capital)
        moic = exit_equity_value / self.equity_investment

        # IRR
        cash_flows = [-self.equity_investment]  # Año 0
        cash_flows.extend([0] * (self.holding_period - 1))  # Años intermedios
        cash_flows.append(exit_equity_value)  # Año final

        # Calcular IRR usando Newton-Raphson
        try:
            irr = self._calculate_irr(cash_flows)
        except:
            irr = None

        # Debt paydown durante holding period
        total_debt_paydown = self.debt_amount - exit_debt

        return {
            'initial_equity_investment': self.equity_investment,
            'exit_equity_value': exit_equity_value,
            'moic': moic,
            'irr': irr,
            'holding_period': self.holding_period,
            'exit_ebitda': exit_ebitda,
            'exit_ev': exit_ev,
            'exit_debt': exit_debt,
            'total_debt_paydown': total_debt_paydown,
            'debt_paydown_pct': total_debt_paydown / self.debt_amount,
            'purchase_multiple': self.purchase_multiple,
            'exit_multiple': self.exit_multiple,
            'ebitda_growth_total': (exit_ebitda / self.purchase_ebitda) - 1
        }

    def _calculate_irr(self, cash_flows: List[float]) -> float:
        """
        Calcula IRR usando NPV = 0

        Args:
            cash_flows: Lista de cash flows

        Returns:
            IRR (en decimal)
        """
        def npv(rate):
            return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))

        def npv_derivative(rate):
            return sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))

        # Usar Newton-Raphson method
        irr = newton(npv, 0.2, fprime=npv_derivative, maxiter=100)
        return irr

    def sensitivity_analysis(
        self,
        exit_multiple_range: tuple = (-1, 1, 0.25),
        ebitda_growth_range: tuple = (-0.05, 0.05, 0.01)
    ) -> Dict:
        """
        Análisis de sensibilidad del IRR

        Args:
            exit_multiple_range: (min_delta, max_delta, step) para exit multiple
            ebitda_growth_range: (min_delta, max_delta, step) para EBITDA growth

        Returns:
            Matriz de sensibilidad
        """
        if not self.debt_schedule:
            raise ValueError("Debe ejecutar calculate_debt_paydown() primero")

        # Rangos
        exit_multiples = np.arange(
            self.exit_multiple + exit_multiple_range[0],
            self.exit_multiple + exit_multiple_range[1] + exit_multiple_range[2],
            exit_multiple_range[2]
        )

        # Calcular average EBITDA growth actual
        avg_growth = (self.ebitda_projections[-1] / self.purchase_ebitda) ** (1 / self.holding_period) - 1

        growth_rates = np.arange(
            avg_growth + ebitda_growth_range[0],
            avg_growth + ebitda_growth_range[1] + ebitda_growth_range[2],
            ebitda_growth_range[2]
        )

        # Matriz de sensibilidad
        irr_matrix = []
        moic_matrix = []

        for exit_mult in exit_multiples:
            irr_row = []
            moic_row = []

            for growth in growth_rates:
                # Calcular exit EBITDA con nuevo growth
                exit_ebitda = self.purchase_ebitda * ((1 + growth) ** self.holding_period)

                # Exit values
                exit_ev = exit_ebitda * exit_mult
                exit_debt = self.debt_schedule[-1]
                exit_equity = exit_ev - exit_debt

                # MOIC
                moic = exit_equity / self.equity_investment
                moic_row.append(moic)

                # IRR
                cash_flows = [-self.equity_investment] + [0] * (self.holding_period - 1) + [exit_equity]
                try:
                    irr = self._calculate_irr(cash_flows)
                    irr_row.append(irr)
                except:
                    irr_row.append(None)

            irr_matrix.append(irr_row)
            moic_matrix.append(moic_row)

        base_returns = self.calculate_returns()

        return {
            'irr_matrix': irr_matrix,
            'moic_matrix': moic_matrix,
            'exit_multiples': exit_multiples.tolist(),
            'ebitda_growth_rates': growth_rates.tolist(),
            'base_case': {
                'irr': base_returns['irr'],
                'moic': base_returns['moic']
            }
        }

    def get_sources_and_uses(self) -> Dict:
        """
        Tabla de Sources & Uses

        Returns:
            Diccionario con sources y uses
        """
        return {
            'uses': {
                'purchase_enterprise_value': self.purchase_price,
                'transaction_fees': 0,  # Puede añadirse
                'total_uses': self.purchase_price
            },
            'sources': {
                'equity_investment': self.equity_investment,
                'debt_financing': self.debt_amount,
                'total_sources': self.equity_investment + self.debt_amount
            },
            'leverage': {
                'debt_to_equity': self.debt_amount / self.equity_investment,
                'debt_to_total_capital': self.debt_amount / (self.equity_investment + self.debt_amount),
                'debt_to_ebitda': self.debt_amount / self.purchase_ebitda
            }
        }

    def __repr__(self) -> str:
        """Representación en string"""
        if self.debt_schedule:
            returns = self.calculate_returns()
            return (
                f"LBOModel(\n"
                f"  Purchase Price: ${self.purchase_price:,.0f}\n"
                f"  Equity Investment: ${self.equity_investment:,.0f}\n"
                f"  Debt: ${self.debt_amount:,.0f}\n"
                f"  Leverage: {self.debt_amount / self.equity_investment:.1f}x\n"
                f"  Holding Period: {self.holding_period} years\n"
                f"  IRR: {returns['irr']:.2%}\n"
                f"  MOIC: {returns['moic']:.2f}x\n"
                f")"
            )
        else:
            return (
                f"LBOModel(\n"
                f"  Purchase Price: ${self.purchase_price:,.0f}\n"
                f"  Equity: ${self.equity_investment:,.0f} | Debt: ${self.debt_amount:,.0f}\n"
                f"  Note: Run project_financials() and calculate_debt_paydown() to calculate returns\n"
                f")"
            )
