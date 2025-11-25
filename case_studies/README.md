# Case Studies - Archivos

Esta carpeta contiene los archivos (Excel, PDF, PowerPoint) de tus case studies que se mostrarán en la app.

## Estructura

```
case_studies/
├── exxon/          # ExxonMobil - DCF & Scenario Analysis
├── mondragon/      # Mondragón University - Sell-Side Case
├── cirsa/          # Cirsa - Gaming/Leisure IPO
└── nuclear_spain/  # Nuclear Policy Impact - Spain Industrial Analysis
```

## Cómo añadir tus archivos

### 1. Coloca tus archivos en las carpetas correspondientes:

**ExxonMobil (DCF)**:
```
case_studies/exxon/
├── exxon_dcf_model.xlsx
├── investor_presentation.pptx
├── exxon_valuation_summary.pdf
└── sensitivity_analysis.xlsx
```

**Mondragón University**:
```
case_studies/mondragon/
├── mondragon_equity_story.pdf
├── teaser_deck.pptx
├── financial_model.xlsx
└── comps_analysis.xlsx
```

**Cirsa (Gaming)**:
```
case_studies/cirsa/
├── cirsa_ipo_analysis.pdf
├── management_presentation.pptx
├── valuation_model.xlsx
└── industry_comps.xlsx
```

**Nuclear Spain (Policy Analysis)**:
```
case_studies/nuclear_spain/
├── spain_france_energy_comparison.xlsx
├── metal_sector_impact_analysis.pptx
├── policy_recommendations.pdf
└── cost_structure_model.xlsx
```

### 2. Formatos soportados

✅ **Excel**: `.xlsx`, `.xls`
✅ **PowerPoint**: `.pptx`, `.ppt`
✅ **PDF**: `.pdf`

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
