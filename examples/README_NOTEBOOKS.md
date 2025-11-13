# 📓 Jupyter Notebooks - M&A Valuation

## Nvidia Analysis Storytelling

**Archivo:** `nvidia_analysis_storytelling.ipynb`

### 📖 Descripción

Este notebook presenta un **análisis completo de valoración de Nvidia** en formato storytelling, con gráficas interactivas y comentarios detallados de cada paso del análisis.

### 🎯 Qué Aprenderás

El notebook está estructurado como una historia que te guía a través de:

1. **Conociendo a Nvidia** - Context y overview de la empresa
2. **DCF Analysis** - Valoración por flujos de caja descontados con sensibilidad
3. **Trading Comparables** - Comparación con AMD, Intel, Qualcomm, Broadcom, TSMC
4. **Financial Ratios** - Análisis de rentabilidad, leverage, liquidez, eficiencia
5. **Executive Summary** - Recomendación final de inversión

### 📊 Visualizaciones Incluidas

- Revenue mix pie chart
- Profit margins bar chart
- FCF projection vs PV comparison
- **DCF sensitivity heatmap** (WACC vs Terminal Growth)
- Trading multiples comparison
- **Football field valuation chart**
- Financial ratios por categoría
- Margins evolution over time
- Valuation waterfall
- Bull/Base/Bear scenarios

### 🚀 Cómo Usarlo

#### Opción 1: Jupyter Notebook (Local)

```bash
# Instalar Jupyter
pip install jupyter matplotlib seaborn

# Navegar a la carpeta
cd M-A/examples

# Lanzar Jupyter
jupyter notebook nvidia_analysis_storytelling.ipynb
```

#### Opción 2: JupyterLab

```bash
pip install jupyterlab
cd M-A/examples
jupyter lab
```

#### Opción 3: Google Colab

1. Sube el archivo `.ipynb` a Google Drive
2. Abre con Google Colab
3. Ejecuta todas las celdas

#### Opción 4: VS Code

1. Instala la extensión "Jupyter" en VS Code
2. Abre el archivo `.ipynb`
3. Ejecuta las celdas interactivamente

### 📝 Estructura del Notebook

```
1. Setup e Imports
   - Configuración de visualización
   - Carga de herramientas

2. Capítulo 1: Conociendo a Nvidia
   - Datos clave
   - Revenue breakdown
   - Profit margins

3. Capítulo 2: DCF Valuation
   - Proyección de FCFs
   - Gordon Growth method
   - Exit Multiple method
   - Sensitivity Analysis (heatmap)

4. Capítulo 3: Trading Comparables
   - 5 peers comparison
   - Multiples analysis
   - Football field chart
   - Premium justification

5. Capítulo 4: Financial Ratios
   - 3 años de datos históricos
   - Profitability ratios
   - Leverage ratios
   - Liquidity ratios
   - Efficiency ratios
   - Growth metrics
   - Benchmark vs industria

6. Resumen Ejecutivo
   - Consolidación de valoraciones
   - Price targets
   - Recomendación final
```

### 🎨 Features del Notebook

✅ **Storytelling**: Narrativa que explica cada paso
✅ **Gráficas profesionales**: Matplotlib + Seaborn
✅ **Análisis interpretado**: No solo números, sino insights
✅ **Datos reales**: Aproximados de Nvidia 2024
✅ **Interactivo**: Puedes modificar assumptions y re-ejecutar
✅ **Educativo**: Aprende valoración haciendo

### 💡 Cómo Personalizar

Puedes adaptar el notebook para analizar otras empresas:

1. **Cambiar datos de entrada**:
   ```python
   # En lugar de Nvidia, usa datos de tu empresa
   target_revenue = 60000  # Cambiar por tu empresa
   target_ebitda = 35000   # Cambiar por tu empresa
   ```

2. **Modificar comparables**:
   ```python
   # Añadir/quitar peers relevantes
   multiples.add_comparable(
       name="Tu Peer",
       enterprise_value=XXX,
       revenue=XXX,
       ebitda=XXX
   )
   ```

3. **Ajustar assumptions DCF**:
   ```python
   # Cambiar growth rates, WACC, etc.
   fcf_projections = [...]  # Tu proyección
   wacc = 0.XX              # Tu WACC
   ```

### 📚 Conceptos que Aprenderás

- **DCF**: Cómo proyectar FCF y calcular terminal value
- **Sensitivity Analysis**: Por qué es crítico variar assumptions
- **Trading Comps**: Cómo seleccionar peers y calcular múltiplos
- **Football Field**: Visualizar rangos de valoración
- **Financial Ratios**: Qué ratios importan en M&A
- **Valuation Synthesis**: Cómo consolidar múltiples métodos

### 🎓 Casos de Uso

Este notebook es perfecto para:

- 📊 **Estudiantes de finanzas** - Aprender valoración práctica
- 💼 **Analistas** - Template para análisis de empresas
- 🏦 **Investment bankers** - Quick analysis framework
- 💰 **Inversores** - Due diligence de inversiones
- 🎯 **Entrepreneurs** - Valorar tu startup o target M&A

### ⚡ Tips

1. **Ejecuta celda por celda** - No hagas "Run All" la primera vez
2. **Lee los comentarios** - Cada sección tiene insights clave
3. **Experimenta con datos** - Cambia números y ve qué pasa
4. **Exporta gráficas** - Click derecho → Save image
5. **Toma notas** - Añade tus propias celdas markdown

### 🐛 Troubleshooting

**Error: "ModuleNotFoundError: No module named 'models'"**
```python
# Asegúrate de estar en la carpeta correcta
import os
os.getcwd()  # Debe ser .../M-A/examples
```

**Error: "No module named matplotlib"**
```bash
pip install matplotlib seaborn
```

**Gráficas no se ven**
```python
%matplotlib inline  # Añadir al inicio
```

### 📖 Recursos Adicionales

- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [DCF Valuation Guide](https://www.investopedia.com/terms/d/dcf.asp)
- [Trading Comps Methodology](https://www.wallstreetoasis.com/resources/skills/valuation/comparable-company-analysis)

---

**¿Preguntas?** Abre un issue en GitHub o contacta al equipo.

**¿Mejoras?** Pull requests bienvenidos!
