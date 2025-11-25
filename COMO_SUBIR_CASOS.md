# 📂 Cómo Subir tus Casos Prácticos (Excel, PDF y PowerPoint)

## Paso 1: Coloca tus archivos en las carpetas correspondientes

### Estructura actual:
```
case_studies/
├── exxon/          # ExxonMobil - DCF & Scenario Analysis
├── mondragon/      # Mondragón University - Sell-Side Case
└── cirsa/          # Cirsa - Gaming/Leisure IPO
```

### Ejemplo con archivos:
```
case_studies/
├── exxon/
│   ├── exxon_dcf_model.xlsx
│   ├── sensitivity_analysis.xlsx
│   ├── investor_presentation.pptx
│   └── valuation_summary.pdf
├── mondragon/
│   ├── mondragon_equity_story.pdf
│   ├── teaser_deck.pptx
│   ├── financial_model.xlsx
│   └── comps_analysis.xlsx
└── cirsa/
    ├── cirsa_ipo_analysis.pdf
    ├── management_presentation.pptx
    └── valuation_model.xlsx
```

## Paso 2: Copia tus archivos

**Opción A - Desde terminal:**
```bash
# Ejemplo: copiar tu Excel de Exxon
cp /ruta/a/tu/archivo/exxon_dcf.xlsx case_studies/exxon/

# Ejemplo: copiar PowerPoint de Exxon
cp /ruta/a/tu/archivo/investor_presentation.pptx case_studies/exxon/

# Ejemplo: copiar PDF de Mondragón
cp /ruta/a/tu/archivo/mondragon_teaser.pdf case_studies/mondragon/
```

**Opción B - Desde GUI:**
1. Navega a la carpeta del proyecto `M-A/`
2. Entra en `case_studies/[nombre_caso]/`
3. Arrastra y suelta tus archivos

## Paso 3: Verifica que se han copiado bien

```bash
# Ver archivos en cada carpeta
ls -la case_studies/exxon/
ls -la case_studies/mondragon/
ls -la case_studies/cirsa/
```

## Paso 4: Commit y Push

```bash
# Añadir todos los archivos nuevos
git add case_studies/

# Ver qué se va a subir
git status

# Commit
git commit -m "Add case study files (Excel, PDF and PowerPoint)"

# Push al repo
git push
```

## Paso 5: Espera 1-2 minutos

Streamlit Cloud detectará los cambios automáticamente y re-deployará la app.

## ✅ ¿Cómo se verán en la app?

En cada tab de "Deal Case Studies", verás:

### 📎 Case Materials

**📊 Excel Models**
- `exxon_dcf_model.xlsx` ⬇️ Download
  - 👁️ Preview: exxon_dcf_model.xlsx (expandible)

**📊 PowerPoint Presentations**
- `investor_presentation.pptx` ⬇️ Download

**📄 PDF Documents**
- `valuation_summary.pdf` ⬇️ Download

## 🎨 Formatos Soportados

✅ **Excel**: `.xlsx`, `.xls`
✅ **PowerPoint**: `.pptx`, `.ppt`
✅ **PDF**: `.pdf`

## 💡 Tips

### Nombres de archivos recomendados:
✅ **Buenos**:
- `DCF_Model_Final.xlsx`
- `Valuation_Summary.pdf`
- `Investor_Presentation.pptx`
- `Teaser_Deck.pptx`
- `Comps_Analysis.xlsx`
- `Sensitivity_Tables.xlsx`

❌ **Evita**:
- `modelo_v23_final_FINAL_2.xlsx`
- `sin título (1).pdf`
- `Presentación1.pptx`
- Nombres con caracteres especiales o espacios

### Privacidad:
⚠️ **IMPORTANTE**: Si tu repo de GitHub es público, los archivos que subas también serán públicos.

**Opciones si tienes info confidencial**:
1. **Sanitiza los datos**: Anonimiza nombres, cifras sensibles
2. **Repo privado**: Haz el repo privado en GitHub (la app seguirá siendo pública)
3. **Versiones demo**: Crea versiones "demo" de tus modelos sin info real

### Tamaño de archivos:
- **Límite de Streamlit Cloud**: ~1 GB total para todo el repo
- **Recomendado para Excels**: < 10 MB cada uno
- **Recomendado para PowerPoint**: < 15 MB cada uno
- **Recomendado para PDFs**: < 5 MB cada uno

Si tus archivos son muy grandes:
- Comprime los PDFs (hay herramientas online gratis)
- Limpia los Excels (elimina hojas no usadas, formatos innecesarios)
- Comprime imágenes en PowerPoint (clic derecho en imagen > Comprimir imágenes)

## 🔧 Troubleshooting

### "No files uploaded yet for..."
Asegúrate de que:
1. Los archivos están en la carpeta correcta (`case_studies/exxon/`, no en `case_studies/`)
2. Tienen la extensión correcta (`.xlsx`, `.xls`, `.pdf`)
3. Hiciste commit y push de los archivos
4. Streamlit Cloud ha terminado de re-deployar (espera 2 min)

### "Cannot preview this file"
- Normal para algunos Excels con macros o fórmulas complejas
- El **download seguirá funcionando** perfectamente
- Solo afecta al preview, no a la funcionalidad

### Los archivos no aparecen tras push
1. Verifica en GitHub que los archivos se hayan subido
2. Ve a Streamlit Cloud > "Manage app" > "Reboot app"
3. Espera 1-2 minutos

## 📁 Crear nuevos casos

Si quieres añadir un nuevo caso (ej: "blackrock"):

```bash
# 1. Crear carpeta
mkdir case_studies/blackrock

# 2. Añadir archivos
cp /ruta/blackrock_model.xlsx case_studies/blackrock/

# 3. Editar app.py para añadir un nuevo tab (o contacta conmigo para ayudarte)
```

## ¿Necesitas ayuda?

Si tienes problemas o quieres añadir funcionalidad nueva:
- Abre un issue en GitHub
- O dime y te ayudo a configurarlo
