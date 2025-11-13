"""
Ejemplo de uso del modelo de Análisis de Múltiplos
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.multiples import MultiplesAnalysis


def main():
    print("=" * 70)
    print("EJEMPLO: Análisis de Múltiplos (Trading Comps)")
    print("=" * 70)
    print()

    # Inicializar análisis
    multiples = MultiplesAnalysis()

    # Añadir empresas comparables
    print("Añadiendo empresas comparables...")
    print()

    multiples.add_comparable(
        name="Comparable A",
        enterprise_value=1500,
        revenue=1000,
        ebitda=200,
        net_income=100,
        market_cap=1300
    )

    multiples.add_comparable(
        name="Comparable B",
        enterprise_value=2000,
        revenue=1200,
        ebitda=250,
        net_income=130,
        market_cap=1800
    )

    multiples.add_comparable(
        name="Comparable C",
        enterprise_value=1800,
        revenue=1100,
        ebitda=220,
        net_income=110,
        market_cap=1600
    )

    multiples.add_comparable(
        name="Comparable D",
        enterprise_value=2200,
        revenue=1400,
        ebitda=280,
        net_income=150,
        market_cap=2000
    )

    # Summary de comparables
    print("RESUMEN DE COMPARABLES:")
    print("-" * 70)

    summary = multiples.get_summary()
    print(f"Total Comparables: {summary['total_comparables']}")
    print()

    for mult_name, stats in summary['multiples_statistics'].items():
        print(f"{mult_name.upper()}:")
        print(f"  Median: {stats['median']:.2f}x")
        print(f"  Mean: {stats['mean']:.2f}x")
        print(f"  Range: {stats['min']:.2f}x - {stats['max']:.2f}x")
        print()

    # Valoración del target
    print("\n" + "=" * 70)
    print("VALORACIÓN DEL TARGET")
    print("=" * 70)
    print()

    valuation = multiples.calculate_valuation(
        target_revenue=1250,
        target_ebitda=240,
        target_net_income=125,
        net_debt=200,
        shares_outstanding=1000,
        statistic='median'  # Usar mediana de los comparables
    )

    print("Valoración por método:")
    print("-" * 70)

    for method, values in valuation.items():
        if method == 'average':
            continue

        print(f"\n{method.upper()}:")
        print(f"  Enterprise Value: ${values.get('enterprise_value', 'N/A'):,.0f}"
              if 'enterprise_value' in values else "")
        print(f"  Equity Value: ${values['equity_value']:,.0f}")
        print(f"  Value per Share: ${values.get('value_per_share', 'N/A'):.2f}"
              if 'value_per_share' in values else "")
        print(f"  Multiple Used: {values['multiple_used']:.2f}x")
        print(f"  Comparables: {values['comparables_count']}")

    if 'average' in valuation:
        print(f"\n{'AVERAGE (ALL METHODS)':}")
        print(f"  Equity Value: ${valuation['average']['equity_value']:,.0f}")
        print(f"  Value per Share: ${valuation['average'].get('value_per_share', 'N/A'):.2f}"
              if 'value_per_share' in valuation['average'] else "")

    # Football Field Analysis
    print("\n\n" + "=" * 70)
    print("FOOTBALL FIELD ANALYSIS")
    print("=" * 70)
    print()

    football_field = multiples.football_field_analysis(
        target_revenue=1250,
        target_ebitda=240,
        target_net_income=125,
        net_debt=200,
        shares_outstanding=1000
    )

    for method, ranges in football_field.items():
        print(f"\n{method.upper()}:")
        print(f"  Equity Value Range: ${ranges['min_equity_value']:,.0f} - ${ranges['max_equity_value']:,.0f}")
        if 'min_value_per_share' in ranges:
            print(f"  Value per Share Range: ${ranges['min_value_per_share']:.2f} - ${ranges['max_value_per_share']:.2f}")
        print(f"  Multiple Range: {ranges['multiple_range'][0]:.2f}x - {ranges['multiple_range'][1]:.2f}x")


if __name__ == "__main__":
    main()
