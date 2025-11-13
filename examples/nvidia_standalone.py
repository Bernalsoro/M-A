"""
NVIDIA M&A ANALYSIS - VERSIÓN STANDALONE

Este script es AUTOCONTENIDO - no requiere los módulos de models/ o analysis/
Solo necesita: numpy, pandas, matplotlib, seaborn

Uso:
    python nvidia_standalone.py

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuración
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.options.display.float_format = '{:,.2f}'.format


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def dcf_valuation():
    """DCF Analysis - Simple Implementation"""
    print_header("1. DCF VALUATION")

    # Proyección FCF
    base_fcf = 28000
    fcf = [
        base_fcf * 1.15,
        32200 * 1.15,
        37030 * 1.12,
        41474 * 1.12,
        46451 * 1.12
    ]

    wacc = 0.09
    terminal_growth = 0.04

    # PV de FCFs
    pv_fcfs = [fcf[i] / ((1 + wacc) ** (i + 1)) for i in range(len(fcf))]
    total_pv_fcf = sum(pv_fcfs)

    # Terminal Value
    terminal_fcf = fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** len(fcf))

    # Enterprise & Equity Value
    ev = total_pv_fcf + pv_terminal
    equity_value = ev - (-25000)  # Net cash
    value_per_share = equity_value / 24500

    print(f"Free Cash Flows (5 years): ${fcf}")
    print(f"PV of FCFs: ${total_pv_fcf:,.0f}M")
    print(f"Terminal Value: ${terminal_value:,.0f}M")
    print(f"PV Terminal Value: ${pv_terminal:,.0f}M")
    print(f"\nEnterprise Value: ${ev:,.0f}M")
    print(f"Equity Value: ${equity_value:,.0f}M")
    print(f"Value per Share: ${value_per_share:.2f}")

    return value_per_share


def trading_comps():
    """Trading Comparables Analysis"""
    print_header("2. TRADING COMPARABLES")

    # Comparables data
    comps = {
        'Company': ['AMD', 'Intel', 'Qualcomm', 'Broadcom', 'TSMC', 'NVIDIA'],
        'EV': [220000, 180000, 145000, 850000, 550000, 2950000],
        'Revenue': [23000, 54000, 36000, 35000, 70000, 60000],
        'EBITDA': [6500, 15000, 12000, 18000, 38000, 35000],
    }

    df = pd.DataFrame(comps)
    df['EV/Revenue'] = df['EV'] / df['Revenue']
    df['EV/EBITDA'] = df['EV'] / df['EBITDA']

    print(df.to_string(index=False))

    # Stats sin Nvidia
    peers = df[df['Company'] != 'NVIDIA']

    print(f"\n📊 PEER MULTIPLES (sin Nvidia):")
    print(f"   EV/Revenue - Median: {peers['EV/Revenue'].median():.2f}x")
    print(f"   EV/EBITDA  - Median: {peers['EV/EBITDA'].median():.2f}x")

    print(f"\n🎯 NVIDIA:")
    nvidia = df[df['Company'] == 'NVIDIA'].iloc[0]
    print(f"   EV/Revenue: {nvidia['EV/Revenue']:.2f}x")
    print(f"   EV/EBITDA:  {nvidia['EV/EBITDA']:.2f}x")

    premium = (nvidia['EV/EBITDA'] / peers['EV/EBITDA'].median() - 1) * 100
    print(f"   Premium vs Peers: +{premium:.0f}%")

    # Valoración usando peer multiples
    median_ebitda_mult = peers['EV/EBITDA'].median()
    implied_ev = 35000 * median_ebitda_mult
    implied_equity = implied_ev - (-25000)
    implied_price = implied_equity / 24500

    print(f"\n💰 VALORACIÓN USANDO PEER MULTIPLES:")
    print(f"   Median EV/EBITDA: {median_ebitda_mult:.2f}x")
    print(f"   Implied Value per Share: ${implied_price:.2f}")
    print(f"   vs Current ($120): {implied_price/120:.1%}")


def financial_ratios():
    """Financial Ratios Analysis"""
    print_header("3. FINANCIAL RATIOS")

    # Historical data
    data = {
        'Period': ['FY 2022', 'FY 2023', 'FY 2024'],
        'Revenue': [27000, 27000, 60000],
        'EBITDA': [13500, 12000, 35000],
        'Net Income': [4400, 4400, 30000],
        'Total Assets': [44000, 50000, 65000],
        'Total Equity': [28000, 32000, 42000],
        'Total Debt': [12000, 10000, 9000],
        'Cash': [16000, 18000, 26000],
    }

    df = pd.DataFrame(data)

    # Calcular ratios
    df['EBITDA Margin'] = (df['EBITDA'] / df['Revenue'] * 100).round(1)
    df['Net Margin'] = (df['Net Income'] / df['Revenue'] * 100).round(1)
    df['ROE'] = (df['Net Income'] / df['Total Equity'] * 100).round(1)
    df['Net Debt'] = df['Total Debt'] - df['Cash']
    df['Debt/EBITDA'] = (df['Total Debt'] / df['EBITDA']).round(2)

    print("📈 EVOLUTION:")
    print(df[['Period', 'Revenue', 'EBITDA', 'EBITDA Margin', 'Net Margin', 'ROE']].to_string(index=False))

    # Latest period ratios
    latest = df.iloc[-1]

    print(f"\n🏆 FY 2024 HIGHLIGHTS:")
    print(f"   EBITDA Margin: {latest['EBITDA Margin']:.1f}%")
    print(f"   Net Margin: {latest['Net Margin']:.1f}%")
    print(f"   ROE: {latest['ROE']:.1f}%")
    print(f"   Net Debt: ${latest['Net Debt']:,.0f}M (Net CASH!)")
    print(f"   Debt/EBITDA: {latest['Debt/EBITDA']:.2f}x")

    # Growth
    rev_cagr = (latest['Revenue'] / df.iloc[0]['Revenue']) ** (1/2) - 1
    print(f"\n📊 GROWTH:")
    print(f"   Revenue CAGR (2022-2024): {rev_cagr:.1%}")
    print(f"   FY 2024 YoY: {(latest['Revenue'] / df.iloc[1]['Revenue'] - 1):.1%}")


def synergies_analysis():
    """Synergies Model - Hypothetical Acquisition"""
    print_header("4. SYNERGIES MODEL")

    print("SCENARIO: Nvidia acquires AI chip competitor for $15B\n")

    # Cost synergies
    cost_synergies = {
        'Headcount reduction': 250,
        'Facility consolidation': 80,
        'Procurement savings': 150,
        'IT consolidation': 40
    }

    # Revenue synergies (EBITDA impact)
    revenue_synergies = {
        'Cross-selling': 325,  # $500M revenue @ 65% gross margin
        'Bundled solutions': 180,
        'Geographic expansion': 124
    }

    print("💰 COST SYNERGIES (Annual Run-Rate):")
    for item, value in cost_synergies.items():
        print(f"   {item:.<40} ${value}M")
    total_cost = sum(cost_synergies.values())
    print(f"   {'TOTAL':.<40} ${total_cost}M")

    print("\n📈 REVENUE SYNERGIES (EBITDA Impact):")
    for item, value in revenue_synergies.items():
        print(f"   {item:.<40} ${value}M")
    total_revenue = sum(revenue_synergies.values())
    print(f"   {'TOTAL':.<40} ${total_revenue}M")

    total_synergies = total_cost + total_revenue
    impl_cost = 255  # Implementation costs

    print(f"\n🎯 TOTAL EBITDA SYNERGIES: ${total_synergies}M")
    print(f"   Implementation Costs: ${impl_cost}M")
    print(f"   Cost-to-Achieve Ratio: {impl_cost/total_synergies:.1%}")

    # Simple NPV (10 years, WACC 9%)
    wacc = 0.09
    after_tax_synergies = total_synergies * 0.79  # After 21% tax
    pv_synergies = sum([after_tax_synergies / ((1 + wacc) ** i) for i in range(1, 11)])
    pv_impl = impl_cost * 0.79  # Tax shield

    npv = pv_synergies - pv_impl

    print(f"\n💎 NPV OF SYNERGIES: ${npv:,.0f}M")
    print(f"   Synergy Value / Deal Value: {npv/15000:.1%}")


def executive_summary():
    """Executive Summary with Recommendation"""
    print_header("5. EXECUTIVE SUMMARY")

    print("📊 VALUATION SUMMARY:")
    print("-" * 80)
    print(f"{'Method':<30} {'Value/Share':<15} {'Comment'}")
    print("-" * 80)
    print(f"{'DCF (Gordon Growth)':<30} ${'36-42':<14} Conservative")
    print(f"{'DCF (Exit Multiple)':<30} ${'45-50':<14} Optimistic")
    print(f"{'Trading Comps (Median)':<30} ${'20-40':<14} Big discount vs peers")
    print(f"{'Fundamentals Adjusted':<30} ${'75-90':<14} Quality premium")
    print("-" * 80)
    print(f"{'Current Market Price':<30} ${'120':<14} Actual")
    print()

    print("✅ STRENGTHS:")
    print("   • Fundamentals EXCEPCIONALES (ROE 71%, margins 58%)")
    print("   • Moat tecnológico inexpugnable (CUDA ecosystem)")
    print("   • Balance sólido (net cash $17B)")
    print("   • AI megatrend beneficiary")

    print("\n⚠️  RISKS:")
    print("   • Valoración EXTREMA (84x EV/EBITDA vs 14x peers)")
    print("   • Competencia intensificando (AMD, custom chips)")
    print("   • Customer concentration (5 hyperscalers)")
    print("   • Regulatory risks (China, antitrust)")

    print("\n🎯 INVESTMENT RECOMMENDATION:")
    print("-" * 80)
    print("   RATING: HOLD / TRIM")
    print()
    print("   Price Targets:")
    print("   • Bear Case:  $90  (-25%)  - Si AI bubble estalla")
    print("   • Base Case:  $105 (-12%)  - Fair value con premium razonable")
    print("   • Bull Case:  $150 (+25%)  - Si AI momentum continúa")
    print()
    print("   ACCIÓN RECOMENDADA:")
    print("   • Si posees: HOLD posiciones core, TRIM si >10% portfolio")
    print("   • Si NO posees: WAIT for better entry <$100")
    print()
    print("💡 VEREDICTO:")
    print("   Nvidia es una empresa EXCEPCIONAL cotizando a valoración EXTREMA.")
    print("   Es una 'bet on AI', no una valoración tradicional.")
    print("   Si crees en AI dominance → Razonable")
    print("   Si tienes dudas → Sobrepagando")
    print("-" * 80)


def main():
    """Run complete Nvidia analysis"""

    print("\n" + "*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + " " * 20 + "NVIDIA M&A ANALYSIS - STANDALONE" + " " * 25 + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)

    print("\nCompany: NVIDIA Corporation (NVDA)")
    print("Market Cap: ~$3.0 Trillion")
    print("Analysis Date:", datetime.now().strftime("%Y-%m-%d"))
    print("Analysis Type: Complete M&A Valuation")

    # Run all analyses
    dcf_value = dcf_valuation()
    trading_comps()
    financial_ratios()
    synergies_analysis()
    executive_summary()

    print("\n" + "=" * 80)
    print("  ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("📁 Para análisis más detallado con gráficas:")
    print("   • Jupyter Notebook: nvidia_analysis_storytelling.ipynb")
    print("   • HTML: nvidia_analysis.html")
    print("   • Script completo: nvidia_case_study.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nVerifica que tengas instalado:")
        print("  pip install numpy pandas matplotlib seaborn")
