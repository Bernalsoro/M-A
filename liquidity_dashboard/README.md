# 🌍 Global Liquidity Dashboard

Dashboard interactivo para **análisis de liquidez global** con actualización automática diaria.

Ideal para analistas financieros, traders y profesionales de banca que necesitan monitorear las condiciones de liquidez del sistema financiero y su relación con los mercados.

---

## 🚀 Características

✅ **Actualización automática diaria** via GitHub Actions
✅ **APIs gratuitas**: FRED (Fed Reserve) + yfinance (Yahoo Finance)
✅ **Dashboard web interactivo** con Streamlit
✅ **Índice de liquidez compuesto** basado en z-scores
✅ **Señales de trading** automáticas
✅ **Regímenes de liquidez** (Crisis, Contraction, Normal, Expansion, Extreme)
✅ **Visualizaciones profesionales** con Plotly

---

## 📊 ¿Qué mide este dashboard?

### Liquidez Global = Capacidad del sistema financiero para sostener precios de activos

El dashboard rastrea:

1. **Fed Balance Sheet** (Total Assets)
2. **Bank Reserves** (Reservas bancarias)
3. **M2 Money Supply** (Oferta monetaria M2)
4. **Treasury General Account (TGA)**
5. **Overnight Reverse Repo (RRP)**

Y calcula:

- **Net Liquidity** = Fed Assets - TGA - Reverse Repo
- **Liquidity Index** = Z-score compuesto de componentes clave
- **Correlación con mercados**: S&P 500, Bitcoin, Gold, DXY

---

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd M-A/liquidity_dashboard
```

### 2. Instalar dependencias

```bash
pip install -r ../requirements.txt
```

### 3. Obtener API Key de FRED (GRATIS)

1. Regístrate en: https://fred.stlouisfed.org/
2. Obtén tu API key: https://fred.stlouisfed.org/docs/api/api_key.html
3. Configura la variable de entorno:

```bash
# Linux/Mac
export FRED_API_KEY="tu_api_key_aqui"

# Windows
set FRED_API_KEY=tu_api_key_aqui
```

O agrega al archivo `.bashrc` / `.zshrc`:

```bash
echo 'export FRED_API_KEY="tu_api_key_aqui"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🎯 Uso

### Paso 1: Actualizar datos

```bash
cd liquidity_dashboard
python src/update_data.py
```

Esto descarga:
- Series de FRED (semanales)
- Precios de mercado (diarios)
- Calcula indicadores
- Guarda en `data/processed/`

### Paso 2: Ejecutar dashboard

```bash
streamlit run src/dashboard_app.py
```

El dashboard se abrirá en `http://localhost:8501`

---

## 📁 Estructura del Proyecto

```
liquidity_dashboard/
│
├── data/
│   ├── raw/                    # Datos descargados directamente
│   │   ├── fred_series.csv
│   │   └── market_prices.csv
│   └── processed/              # Datos procesados listos para dashboard
│       ├── liquidity_data.csv
│       ├── market_prices.csv
│       ├── market_prices_weekly.csv
│       └── summary.csv
│
├── src/
│   ├── config.py               # Configuración de APIs y tickers
│   ├── fetch_fred.py           # Descargar datos de FRED
│   ├── fetch_market.py         # Descargar precios de mercado
│   ├── transform.py            # Funciones de transformación (z-scores, etc.)
│   ├── indicators.py           # Índice de liquidez y señales
│   ├── update_data.py          # Script de actualización (ejecutar diariamente)
│   └── dashboard_app.py        # Dashboard Streamlit
│
└── README.md                   # Este archivo
```

---

## 🤖 Actualización Automática con GitHub Actions

Para que el dashboard se actualice **automáticamente cada día**:

### 1. Configurar Secret en GitHub

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Nombre: `FRED_API_KEY`
5. Valor: Tu API key de FRED
6. Save

### 2. El workflow ya está configurado

El archivo `.github/workflows/update-liquidity-data.yml` ya está creado y:

- ✅ Se ejecuta **todos los días a las 02:00 UTC** (después del cierre de mercados)
- ✅ Descarga datos actualizados
- ✅ Hace commit y push automático
- ✅ También se puede ejecutar **manualmente** desde GitHub UI

### 3. Ejecutar manualmente (opcional)

En GitHub:
1. Actions → Update Liquidity Data
2. Run workflow → Run workflow

---

## 📈 Datos que rastrea

### Fuente: FRED (Federal Reserve)

| Serie | ID FRED | Descripción |
|-------|---------|-------------|
| Fed Total Assets | `WALCL` | Balance total de la Fed |
| Bank Reserves | `WRESBAL` | Reservas bancarias |
| Treasury General Account | `WTREGEN` | Cuenta del Tesoro en la Fed |
| Overnight Reverse Repo | `RRPONTSYD` | RRP overnight |
| M2 Money Supply | `WM2NS` | Oferta monetaria M2 |

### Fuente: Yahoo Finance (yfinance)

| Activo | Ticker | Descripción |
|--------|--------|-------------|
| S&P 500 | `^GSPC` | Índice bursátil US |
| NASDAQ | `^IXIC` | Índice tech |
| Bitcoin | `BTC-USD` | Criptomoneda |
| Gold | `GC=F` | Oro (futuros) |
| US Dollar Index | `DX-Y.NYB` | Índice del dólar |
| 10Y Treasury Yield | `^TNX` | Rendimiento bono 10 años |

---

## 🧮 Fórmulas Clave

### Net Liquidity

```
Net Liquidity = Fed Total Assets - TGA - Reverse Repo
```

Esta es la métrica que muchos traders siguen porque representa la liquidez "real" disponible en el sistema.

### Liquidity Index

```
Liquidity Index = mean(z_score(Fed Assets), z_score(Reserves), z_score(M2))
```

Promedio de z-scores normalizados. Valores:
- `> 1.5`: Expansión extrema
- `0.5 - 1.5`: Expansión
- `-0.5 - 0.5`: Normal
- `-1.5 - -0.5`: Contracción
- `< -1.5`: Crisis

### Trading Signals

```
Signal = 1  (Buy)    si z-score > 0.5
Signal = 0  (Neutral) si -0.5 ≤ z-score ≤ 0.5
Signal = -1 (Sell)   si z-score < -0.5
```

---

## 🎨 Screenshots del Dashboard

El dashboard incluye:

1. **Key Metrics**: Última actualización, Net Liquidity, Liquidity Index, Régimen
2. **Liquidity vs Market**: Gráfico dual normalizado (liquidez + S&P 500)
3. **Fed Components**: Evolución de componentes del balance de la Fed
4. **Liquidity Regime**: Clasificación histórica del régimen
5. **Market Overview**: Todos los activos normalizados

---

## 💡 Casos de Uso

### Para analistas de M&A
- Evaluar condiciones de mercado antes de operaciones
- Timing de IPOs y salidas
- Análisis de valuación en contexto macro

### Para traders
- Identificar regímenes de "risk-on" vs "risk-off"
- Correlación liquidez-precio para timing
- Señales de entrada/salida basadas en condiciones sistémicas

### Para presentaciones
- Dashboard profesional para mostrar en procesos de selección
- Actualización automática = siempre actualizado
- Gráficos interactivos exportables

---

## 🔄 Mantenimiento

### Actualización manual de datos

```bash
python src/update_data.py
```

### Modificar tickers o series

Edita `src/config.py`:

```python
MARKET_TICKERS = {
    "tu_activo": "TICKER",  # Agrega aquí
}

FRED_SERIES = {
    "tu_serie": "SERIE_ID",  # Agrega aquí
}
```

### Cambiar frecuencia de actualización

Edita `.github/workflows/update-liquidity-data.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Diario a las 02:00 UTC
  # - cron: '0 */6 * * *'  # Cada 6 horas
  # - cron: '0 0 * * 1'    # Semanal (lunes)
```

---

## 🐛 Troubleshooting

### Error: "FRED_API_KEY no configurada"

```bash
export FRED_API_KEY="tu_key_aqui"
python src/update_data.py
```

### Error: "No se encontraron datos"

1. Ejecuta primero `python src/update_data.py`
2. Verifica que exista `data/processed/liquidity_data.csv`

### GitHub Actions no actualiza

1. Verifica que `FRED_API_KEY` esté en GitHub Secrets
2. Revisa Actions → Workflow runs para ver errores

---

## 📚 Recursos

- **FRED API Docs**: https://fred.stlouisfed.org/docs/api/
- **yfinance Docs**: https://pypi.org/project/yfinance/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Plotly Docs**: https://plotly.com/python/

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Notas

- Los datos de FRED son **semanales** (miércoles)
- Los datos de mercado son **diarios**
- El dashboard resamplea a semanal para alinear
- GitHub Actions usa **Ubuntu** (Linux)
- El cache de pip reduce tiempo de ejecución

---

## 📧 Contacto

Para preguntas, abre un issue en GitHub.

---

## ⭐ Si te resulta útil

Dale una estrella ⭐ al repositorio y compártelo con colegas que puedan beneficiarse.

---

**Nota**: Este es un proyecto educativo/profesional. No constituye asesoramiento financiero. Siempre haz tu propia investigación (DYOR).
