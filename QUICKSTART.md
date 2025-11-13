# Quick Start Guide - M&A Valuation Tools

## Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd M-A

# Instalar dependencias
pip install -r requirements.txt

# O instalar el paquete
pip install -e .
```

## Uso Rápido

### 1. Modelo DCF (Discounted Cash Flow)

```python
from models.dcf import DCFModel

# Crear modelo DCF
dcf = DCFModel(
    free_cash_flows=[100, 110, 121, 133, 146],  # FCF proyectados (5 años)
    wacc=0.10,                                   # 10% WACC
    terminal_growth_rate=0.03,                   # 3% crecimiento perpetuo
    net_debt=200,                                # Deuda neta
    shares_outstanding=1000                      # Acciones en circulación
)

# Calcular valoración
valuation = dcf.calculate_valuation()
print(f"Valor por acción: ${valuation['value_per_share']:.2f}")

# Análisis de sensibilidad
sensitivity = dcf.sensitivity_analysis()
```

### 2. Análisis de Múltiplos

```python
from models.multiples import MultiplesAnalysis

# Crear análisis
multiples = MultiplesAnalysis()

# Añadir comparables
multiples.add_comparable(
    name="Comparable A",
    enterprise_value=1500,
    revenue=1000,
    ebitda=200
)

# Valorar target
valuation = multiples.calculate_valuation(
    target_ebitda=240,
    target_revenue=1250,
    net_debt=200
)
```

### 3. Modelo LBO

```python
from models.lbo import LBOModel

# Inicializar LBO
lbo = LBOModel(
    purchase_price=1000,
    purchase_ebitda=150,
    equity_investment=300,
    debt_amount=700,
    interest_rate=0.06,
    holding_period=5,
    exit_multiple=8.0
)

# Proyectar financials
lbo.project_financials(
    ebitda_growth_rates=[0.05, 0.06, 0.06, 0.05, 0.05],
    revenue_growth_rates=[0.08, 0.08, 0.07, 0.07, 0.06],
    capex_pct_of_revenue=[0.04, 0.04, 0.03, 0.03, 0.03]
)

# Calcular debt paydown
lbo.calculate_debt_paydown()

# Calcular returns
returns = lbo.calculate_returns()
print(f"IRR: {returns['irr']:.2%}")
print(f"MOIC: {returns['moic']:.2f}x")
```

### 4. Modelo de Sinergias

```python
from models.synergies import SynergiesModel

# Inicializar
synergies = SynergiesModel(wacc=0.10, tax_rate=0.25)

# Añadir cost synergy
synergies.add_cost_synergy(
    name="Headcount reduction",
    annual_savings=50,
    implementation_cost=10,
    years_to_full_realization=2,
    risk_adjustment=0.9
)

# Añadir revenue synergy
synergies.add_revenue_synergy(
    name="Cross-selling",
    annual_revenue_increase=80,
    cost_of_revenue_pct=0.60,
    implementation_cost=15,
    years_to_full_realization=3
)

# Valorar sinergias
valuation = synergies.calculate_synergy_value()
print(f"Valor NPV de sinergias: ${valuation['total_synergy_value']:,.0f}")
```

### 5. Análisis de Ratios Financieros

```python
from analysis.financial_ratios import FinancialRatiosAnalysis

# Inicializar
ratios = FinancialRatiosAnalysis()

# Añadir período
ratios.add_period(
    period_name="2023",
    revenue=1000,
    ebitda=200,
    net_income=100,
    total_assets=1500,
    total_equity=800
)

# Calcular ratios
all_ratios = ratios.calculate_all_ratios()
print(all_ratios)
```

### 6. Due Diligence Financiero

```python
from analysis.due_diligence import DueDiligenceAnalysis

# Inicializar
dd = DueDiligenceAnalysis()

# Añadir períodos
dd.add_period(
    period_name="2023",
    revenue=1000,
    gross_profit=400,
    ebitda=200,
    net_income=100,
    operating_cash_flow=150
)

# Identificar red flags
red_flags = dd.get_all_red_flags()
print(f"Red flags encontrados: {red_flags['total_issues']}")

# Generar reporte
report = dd.generate_due_diligence_report()
print(report)
```

## Ejemplos Completos

Revisar la carpeta `examples/` para ejemplos detallados:

- `dcf_example.py` - DCF completo con sensibilidad
- `lbo_example.py` - LBO con debt schedule
- `multiples_example.py` - Trading comps y football field
- `synergies_example.py` - Valoración de sinergias

## Ejecutar Ejemplos

```bash
# DCF
python examples/dcf_example.py

# LBO
python examples/lbo_example.py

# Múltiplos
python examples/multiples_example.py

# Sinergias
python examples/synergies_example.py
```

## Documentación

Para documentación completa, revisar:
- `README.md` - Overview del proyecto
- Docstrings en cada módulo
- Ejemplos en `/examples`

## Soporte

Para preguntas o issues, abrir un issue en GitHub.
