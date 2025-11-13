"""
Ejemplo de uso del modelo de Sinergias
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.synergies import SynergiesModel


def main():
    print("=" * 70)
    print("EJEMPLO: Modelo de Sinergias")
    print("=" * 70)
    print()

    # Inicializar modelo
    synergies = SynergiesModel(
        wacc=0.10,  # 10% WACC para descontar
        tax_rate=0.25  # 25% tax rate
    )

    # Añadir cost synergies
    print("Añadiendo Cost Synergies...")
    print()

    synergies.add_cost_synergy(
        name="Headcount reduction",
        annual_savings=50,  # $50M/año
        implementation_cost=10,  # $10M one-time
        years_to_full_realization=2,
        realization_curve='linear',
        risk_adjustment=0.9  # 90% confianza
    )

    synergies.add_cost_synergy(
        name="Facility consolidation",
        annual_savings=30,
        implementation_cost=5,
        years_to_full_realization=3,
        realization_curve='hockey_stick',
        risk_adjustment=0.85
    )

    synergies.add_cost_synergy(
        name="Procurement savings",
        annual_savings=25,
        implementation_cost=2,
        years_to_full_realization=1,
        realization_curve='immediate',
        risk_adjustment=0.95
    )

    # Añadir revenue synergies
    print("Añadiendo Revenue Synergies...")
    print()

    synergies.add_revenue_synergy(
        name="Cross-selling to combined customer base",
        annual_revenue_increase=80,  # $80M revenue incremental
        cost_of_revenue_pct=0.60,  # 60% COGS
        implementation_cost=15,
        years_to_full_realization=3,
        realization_curve='linear',
        risk_adjustment=0.70  # Más conservador para revenue synergies
    )

    synergies.add_revenue_synergy(
        name="Geographic expansion",
        annual_revenue_increase=50,
        cost_of_revenue_pct=0.55,
        implementation_cost=10,
        years_to_full_realization=4,
        realization_curve='hockey_stick',
        risk_adjustment=0.65
    )

    # Resumen de sinergias
    print("\n" + "=" * 70)
    print("RESUMEN DE SINERGIAS")
    print("=" * 70)
    print()

    summary = synergies.get_synergies_summary()

    print(f"COST SYNERGIES ({summary['cost_synergies']['count']}):")
    print("-" * 70)
    print(f"Total Run-Rate: ${summary['cost_synergies']['total_run_rate']:,.0f}")
    for item in summary['cost_synergies']['items']:
        print(f"\n  {item['name']}:")
        print(f"    Annual Savings: ${item['annual_savings']:,.0f}")
        print(f"    Implementation Cost: ${item['implementation_cost']:,.0f}")
        print(f"    Years to Realize: {item['years_to_realize']}")

    print(f"\n\nREVENUE SYNERGIES ({summary['revenue_synergies']['count']}):")
    print("-" * 70)
    print(f"Total Run-Rate EBITDA: ${summary['revenue_synergies']['total_run_rate_ebitda']:,.0f}")
    for item in summary['revenue_synergies']['items']:
        print(f"\n  {item['name']}:")
        print(f"    Annual Revenue: ${item['annual_revenue']:,.0f}")
        print(f"    Annual EBITDA: ${item['annual_ebitda']:,.0f}")
        print(f"    Implementation Cost: ${item['implementation_cost']:,.0f}")
        print(f"    Years to Realize: {item['years_to_realize']}")

    print("\n\nTOTALS:")
    print("-" * 70)
    print(f"Total EBITDA Run-Rate: ${summary['totals']['total_ebitda_run_rate']:,.0f}")
    print(f"Total Implementation Costs: ${summary['totals']['total_implementation_costs']:,.0f}")
    print(f"Cost-to-Achieve Ratio: {summary['totals']['cost_to_achieve_ratio']:.1%}")

    # Valoración de sinergias
    print("\n\n" + "=" * 70)
    print("VALORACIÓN DE SINERGIAS (NPV)")
    print("=" * 70)
    print()

    valuation = synergies.calculate_synergy_value(
        projection_years=10,
        terminal_growth_rate=0.0  # Conservador: sin crecimiento post-período
    )

    print(f"Total Synergy Value (NPV): ${valuation['total_synergy_value']:,.0f}")
    print(f"  PV of Projection Period: ${valuation['pv_projection_period']:,.0f}")
    print(f"  PV of Terminal Value: ${valuation['pv_terminal_value']:,.0f}")
    print()

    print("Run-Rate Sinergias (Año 10):")
    print(f"  Cost Savings: ${valuation['run_rate_synergies']['cost_savings']:,.0f}")
    print(f"  Revenue EBITDA: ${valuation['run_rate_synergies']['revenue_ebitda']:,.0f}")
    print(f"  Total EBITDA: ${valuation['run_rate_synergies']['total_ebitda']:,.0f}")
    print()

    # Risk analysis
    print("\n" + "=" * 70)
    print("ANÁLISIS DE RIESGO")
    print("=" * 70)
    print()

    risk = synergies.synergy_risk_analysis()

    print("Cost Synergies Risk Profile:")
    print(f"  Average Risk Adjustment: {risk['cost_synergies_risk']['average_risk_adjustment']:.1%}")
    print(f"  Range: {risk['cost_synergies_risk']['min_risk_adjustment']:.1%} - "
          f"{risk['cost_synergies_risk']['max_risk_adjustment']:.1%}")
    print()

    print("Revenue Synergies Risk Profile:")
    print(f"  Average Risk Adjustment: {risk['revenue_synergies_risk']['average_risk_adjustment']:.1%}")
    print(f"  Range: {risk['revenue_synergies_risk']['min_risk_adjustment']:.1%} - "
          f"{risk['revenue_synergies_risk']['max_risk_adjustment']:.1%}")
    print()

    print(synergies)


if __name__ == "__main__":
    main()
