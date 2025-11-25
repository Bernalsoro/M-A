# Case Studies - Archivos

Esta carpeta contiene los archivos (Excel, PDF) de tus case studies que se mostrarán en la app.

## Estructura

```
case_studies/
├── exxon/          # ExxonMobil - DCF & Scenario Analysis
├── mondragon/      # Mondragón University - Sell-Side Case
└── cirsa/          # Cirsa - Gaming/Leisure IPO
```

## Cómo añadir tus archivos

### 1. Coloca tus archivos en las carpetas correspondientes:

**ExxonMobil (DCF)**:
```
case_studies/exxon/
├── exxon_dcf_model.xlsx
├── exxon_valuation_summary.pdf
└── sensitivity_analysis.xlsx
```

**Mondragón University**:
```
case_studies/mondragon/
├── mondragon_equity_story.pdf
├── financial_model.xlsx
└── comps_analysis.xlsx
```

**Cirsa (Gaming)**:
```
case_studies/cirsa/
├── cirsa_ipo_analysis.pdf
├── valuation_model.xlsx
└── industry_comps.xlsx
```

### 2. Formatos soportados

✅ **Excel**: `.xlsx`, `.xls`
✅ **PDF**: `.pdf`
✅ **CSV**: `.csv` (opcional)

### 3. Haz commit y push

```bash
git add case_studies/
git commit -m "Add case study files"
git push
```

La app se actualizará automáticamente en Streamlit Cloud.

## Privacidad

⚠️ **IMPORTANTE**: Los archivos que subas al repo serán **públicos** si el repo es público.

Si tienes información confidencial:
- Usa versiones sanitizadas/anonimizadas
- O mantén el repo privado
- O usa la opción de "Upload" en la UI (los archivos no se guardan)

## Nombres recomendados

Para que se vean bien en la app, usa nombres descriptivos:
- ✅ `DCF_Model_Final.xlsx`
- ✅ `Valuation_Summary.pdf`
- ❌ `modelo_v23_final_FINAL_2.xlsx`
