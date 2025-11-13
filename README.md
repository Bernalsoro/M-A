# M&A Valuation Tools

Herramientas profesionales de valoración para Fusiones y Adquisiciones (M&A).

## 🚀 Características

### Herramientas de Valoración
1. **Modelo DCF** (Discounted Cash Flow) - Valoración mediante flujos de caja descontados
2. **Análisis de Múltiplos** - Comparables de mercado (P/E, EV/EBITDA, EV/Sales, etc.)
3. **Análisis de Transacciones Precedentes** - Valoración basada en M&A comparables

### Análisis Financiero
4. **Modelo de Sinergias** - Cálculo y valoración de sinergias de costes e ingresos
5. **Análisis de Due Diligence Financiero** - Análisis de ratios, tendencias y red flags
6. **Modelo LBO** (Leveraged Buyout) - Análisis de retornos con apalancamiento

### Análisis de Datos
7. **Análisis de Ratios Financieros** - KPIs clave para M&A (ROIC, WACC, márgenes, etc.)
8. **Modelo de Integración y Creación de Valor** - Tracking de value creation post-merger

## 📁 Estructura del Proyecto

```
M-A/
├── models/              # Modelos de valoración
│   ├── dcf.py          # Discounted Cash Flow
│   ├── multiples.py    # Análisis de Múltiplos
│   ├── precedent_transactions.py
│   ├── synergies.py    # Modelo de Sinergias
│   ├── lbo.py          # Leveraged Buyout
│   └── integration_value_creation.py
├── analysis/           # Herramientas de análisis
│   ├── financial_ratios.py
│   └── due_diligence.py
├── utils/              # Utilidades comunes
│   ├── wacc.py         # Cálculo WACC
│   ├── terminal_value.py
│   └── data_validation.py
├── examples/           # Ejemplos de uso
└── tests/             # Tests unitarios
```

## 🔧 Instalación

```bash
pip install -r requirements.txt
```

## 💡 Uso Rápido

### DCF (Discounted Cash Flow)

```python
from models.dcf import DCFModel

dcf = DCFModel(
    free_cash_flows=[100, 110, 121, 133, 146],
    wacc=0.10,
    terminal_growth_rate=0.03,
    net_debt=200,
    shares_outstanding=1000
)

valuation = dcf.calculate_valuation()
print(f"Valor por acción: ${valuation['value_per_share']:.2f}")
```

### LBO (Leveraged Buyout)

```python
from models.lbo import LBOModel

lbo = LBOModel(
    purchase_price=1000,
    debt_financing=700,
    ebitda=150,
    exit_multiple=8.0,
    holding_period=5
)

returns = lbo.calculate_returns()
print(f"IRR: {returns['irr']:.2%}")
```

### Análisis de Múltiplos

```python
from models.multiples import MultiplesAnalysis

multiples = MultiplesAnalysis()
multiples.add_comparable("Comp A", ev=1000, ebitda=100, revenue=500)
multiples.add_comparable("Comp B", ev=1500, ebitda=150, revenue=750)

valuation = multiples.calculate_valuation(target_ebitda=120, target_revenue=600)
```

## 📊 Características Principales

- **Modelos Completos**: Implementación profesional de todos los modelos de valoración M&A
- **Flexible**: Fácilmente adaptable a diferentes industrias y escenarios
- **Análisis Sensibilidad**: Análisis de sensibilidad integrado en todos los modelos
- **Documentación**: Código completamente documentado con ejemplos
- **Validación de Datos**: Validación automática de inputs y outputs

## 📈 Módulos Principales

### 1. DCF Model
- Proyecciones de Free Cash Flow
- Cálculo de WACC
- Valor Terminal (Gordon Growth y Exit Multiple)
- Análisis de sensibilidad (WACC vs Terminal Growth)

### 2. LBO Model
- Estructura de capital y apalancamiento
- Cascada de pagos de deuda
- Cálculo de IRR y MOIC (Multiple on Invested Capital)
- Análisis de sensibilidad (Exit Multiple vs EBITDA Growth)

### 3. Synergies Model
- Sinergias de costes (operativas, administrativas)
- Sinergias de ingresos (cross-selling, pricing power)
- Value creation waterfall
- Timeline de realización

### 4. Due Diligence
- Análisis de calidad de earnings
- Detección de red flags
- Análisis de tendencias financieras
- Working capital analysis

## 🛠️ Requisitos

- Python 3.8+
- pandas
- numpy
- scipy
- openpyxl (para Excel)
- matplotlib (para visualizaciones)

## 📝 Licencia

MIT License

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## 📧 Contacto

Para preguntas y soporte, por favor abre un issue en GitHub.
