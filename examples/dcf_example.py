"""
Ejemplo de uso del modelo DCF (Discounted Cash Flow)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.dcf import DCFModel


def main():
    print("=" * 70)
    print("EJEMPLO: Modelo DCF (Discounted Cash Flow)")
    print("=" * 70)
    print()

    # Ejemplo 1: DCF con Gordon Growth
    print("Ejemplo 1: DCF con Gordon Growth Method")
    print("-" * 70)

    dcf = DCFModel(
        free_cash_flows=[100, 110, 121, 133, 146],  # 5 años de proyección
        wacc=0.10,  # 10% WACC
        terminal_growth_rate=0.03,  # 3% crecimiento perpetuo
        net_debt=200,  # $200M de deuda neta
        minority_interest=50,
        shares_outstanding=1000  # 1000M acciones
    )

    print(dcf)
    print()

    # Valoración completa
    valuation = dcf.calculate_valuation()

    print(f"Enterprise Value: ${valuation['enterprise_value']:,.0f}")
    print(f"Equity Value: ${valuation['equity_value']:,.0f}")
    print(f"Value per Share: ${valuation['value_per_share']:,.2f}")
    print(f"PV of FCFs: ${valuation['pv_fcf']:,.0f}")
    print(f"PV of Terminal Value: ${valuation['pv_terminal_value']:,.0f}")
    print(f"Terminal Value %: {(valuation['pv_terminal_value']/valuation['enterprise_value']):.1%}")
    print()

    # Análisis de sensibilidad
    print("Análisis de Sensibilidad (WACC vs Terminal Growth):")
    print("-" * 70)

    sensitivity = dcf.sensitivity_analysis(
        wacc_range=(-0.02, 0.02, 0.005),
        terminal_growth_range=(-0.01, 0.01, 0.005)
    )

    print(f"Base Case Value per Share: ${sensitivity['base_case_value']:.2f}")
    print()
    print("WACC values:", [f"{w:.1%}" for w in sensitivity['wacc_values'][:3]], "...")
    print("Growth values:", [f"{g:.1%}" for g in sensitivity['terminal_growth_values'][:3]], "...")
    print()

    # Ejemplo 2: DCF con Exit Multiple
    print("\n" + "=" * 70)
    print("Ejemplo 2: DCF con Exit Multiple Method")
    print("-" * 70)

    dcf2 = DCFModel(
        free_cash_flows=[100, 110, 121, 133, 146],
        wacc=0.10,
        exit_multiple=8.0,  # 8x EV/EBITDA al exit
        final_year_ebitda=200,  # EBITDA año 5
        net_debt=200,
        shares_outstanding=1000
    )

    valuation2 = dcf2.calculate_valuation()

    print(f"Enterprise Value: ${valuation2['enterprise_value']:,.0f}")
    print(f"Equity Value: ${valuation2['equity_value']:,.0f}")
    print(f"Value per Share: ${valuation2['value_per_share']:,.2f}")
    print()


if __name__ == "__main__":
    main()
