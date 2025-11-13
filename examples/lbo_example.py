"""
Ejemplo de uso del modelo LBO (Leveraged Buyout)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.lbo import LBOModel


def main():
    print("=" * 70)
    print("EJEMPLO: Modelo LBO (Leveraged Buyout)")
    print("=" * 70)
    print()

    # Inicializar LBO
    lbo = LBOModel(
        purchase_price=1000,  # $1000M Enterprise Value
        purchase_ebitda=150,  # $150M EBITDA
        equity_investment=300,  # $300M equity
        debt_amount=700,  # $700M debt
        interest_rate=0.06,  # 6% interest
        holding_period=5,  # 5 años
        exit_multiple=8.0,  # 8x EV/EBITDA al exit
        tax_rate=0.25
    )

    print("SOURCES & USES:")
    print("-" * 70)
    sources_uses = lbo.get_sources_and_uses()

    print(f"Purchase Price: ${sources_uses['uses']['purchase_enterprise_value']:,.0f}")
    print()
    print(f"Equity: ${sources_uses['sources']['equity_investment']:,.0f}")
    print(f"Debt: ${sources_uses['sources']['debt_financing']:,.0f}")
    print()
    print(f"Leverage Metrics:")
    print(f"  Debt/Equity: {sources_uses['leverage']['debt_to_equity']:.2f}x")
    print(f"  Debt/EBITDA: {sources_uses['leverage']['debt_to_ebitda']:.2f}x")
    print()

    # Proyectar financials
    print("PROYECCIÓN FINANCIERA:")
    print("-" * 70)

    lbo.project_financials(
        ebitda_growth_rates=[0.05, 0.06, 0.06, 0.05, 0.05],  # 5-6% growth
        revenue_growth_rates=[0.08, 0.08, 0.07, 0.07, 0.06],
        capex_pct_of_revenue=[0.04, 0.04, 0.03, 0.03, 0.03],
        nwc_pct_of_revenue=0.15
    )

    print("EBITDA Projection:")
    for i, ebitda in enumerate(lbo.ebitda_projections):
        print(f"  Year {i}: ${ebitda:,.0f}")
    print()

    # Calcular debt paydown
    lbo.calculate_debt_paydown(
        mandatory_paydown_pct=0.5,
        cash_sweep_pct=0.75
    )

    print("DEBT SCHEDULE:")
    print("-" * 70)
    for i, debt in enumerate(lbo.debt_schedule):
        print(f"  Year {i}: ${debt:,.0f}")
    print()

    # Calcular returns
    print("RETURNS ANALYSIS:")
    print("=" * 70)

    returns = lbo.calculate_returns()

    print(f"\nInitial Investment: ${returns['initial_equity_investment']:,.0f}")
    print(f"Exit Equity Value: ${returns['exit_equity_value']:,.0f}")
    print()
    print(f"IRR: {returns['irr']:.2%}")
    print(f"MOIC: {returns['moic']:.2f}x")
    print()
    print(f"Exit EBITDA: ${returns['exit_ebitda']:,.0f}")
    print(f"Exit Multiple: {returns['exit_multiple']:.1f}x")
    print(f"Debt Paydown: ${returns['total_debt_paydown']:,.0f} ({returns['debt_paydown_pct']:.1%})")
    print()

    # Análisis de sensibilidad
    print("SENSITIVITY ANALYSIS:")
    print("-" * 70)

    sensitivity = lbo.sensitivity_analysis(
        exit_multiple_range=(-1, 1, 0.5),
        ebitda_growth_range=(-0.02, 0.02, 0.01)
    )

    print(f"Base Case IRR: {sensitivity['base_case']['irr']:.2%}")
    print(f"Base Case MOIC: {sensitivity['base_case']['moic']:.2f}x")
    print()
    print("IRR Sensitivity Matrix (sample):")
    print(f"Exit Multiples: {sensitivity['exit_multiples'][:3]} ...")
    print(f"Growth Rates: {[f'{g:.1%}' for g in sensitivity['ebitda_growth_rates'][:3]]} ...")
    print()

    print(lbo)


if __name__ == "__main__":
    main()
