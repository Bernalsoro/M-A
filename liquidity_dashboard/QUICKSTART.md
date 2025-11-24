# 🚀 Quick Start - Global Liquidity Dashboard

Guía rápida para tener el dashboard funcionando en **5 minutos**.

---

## ⚡ Setup en 5 Pasos

### 1️⃣ Instalar dependencias (30 segundos)

```bash
cd M-A
pip install -r requirements.txt
```

### 2️⃣ Obtener API Key de FRED (2 minutos)

1. Ve a: https://fred.stlouisfed.org/
2. Regístrate (gratis)
3. Obtén tu API key: https://fred.stlouisfed.org/docs/api/api_key.html

### 3️⃣ Configurar la API Key (10 segundos)

```bash
# Linux/Mac
export FRED_API_KEY="tu_api_key_aqui"

# Windows CMD
set FRED_API_KEY=tu_api_key_aqui

# Windows PowerShell
$env:FRED_API_KEY="tu_api_key_aqui"
```

### 4️⃣ Descargar datos (1-2 minutos)

```bash
cd liquidity_dashboard
python src/update_data.py
```

Verás algo como:
```
======================================================================
🌍 GLOBAL LIQUIDITY DASHBOARD - DATA UPDATE
======================================================================

📊 Descargando 5 series de FRED...
  → fed_total_assets (WALCL)... ✅ 832 observaciones
  → bank_reserves (WRESBAL)... ✅ 832 observaciones
  ...

✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO
```

### 5️⃣ Ejecutar dashboard (10 segundos)

```bash
streamlit run src/dashboard_app.py
```

Se abrirá automáticamente en: `http://localhost:8501`

**¡Listo! 🎉**

---

## 📊 ¿Qué verás en el dashboard?

### Key Metrics
- **Last Update**: Última fecha de datos
- **Net Liquidity**: Liquidez neta del sistema ($M)
- **Liquidity Index**: Z-score compuesto
- **Regime**: Crisis / Contraction / Normal / Expansion / Extreme

### Charts
1. **Liquidity vs Market**: Liquidez normalizada vs S&P 500
2. **Fed Components**: Evolución del balance de la Fed
3. **Liquidity Regime**: Régimen histórico de liquidez
4. **Market Overview**: Todos los activos (Bitcoin, Gold, DXY, etc.)

---

## 🤖 Actualización Automática (Opcional)

Para que se actualice **solo cada día**:

### Paso 1: GitHub Secret

En tu repo GitHub:
1. Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `FRED_API_KEY`
4. Value: tu_api_key

### Paso 2: Activar GitHub Actions

El workflow ya está configurado en:
`.github/workflows/update-liquidity-data.yml`

Se ejecuta:
- ✅ Todos los días a las 02:00 UTC
- ✅ O manualmente desde GitHub Actions

---

## 💡 Comandos Útiles

### Actualizar datos manualmente
```bash
cd liquidity_dashboard
python src/update_data.py
```

### Ejecutar dashboard
```bash
cd liquidity_dashboard
streamlit run src/dashboard_app.py
```

### Test rápido (sin API key)
```bash
cd liquidity_dashboard/src
python transform.py  # Test de transformaciones
python indicators.py # Test de indicadores
```

---

## 🐛 Solución de Problemas

### ❌ Error: "FRED_API_KEY no configurada"

**Solución**:
```bash
export FRED_API_KEY="tu_key_aqui"
```

Para que persista (Linux/Mac):
```bash
echo 'export FRED_API_KEY="tu_key"' >> ~/.bashrc
source ~/.bashrc
```

### ❌ Error: "No se encontraron datos"

**Causa**: No has ejecutado `update_data.py`

**Solución**:
```bash
python src/update_data.py
```

### ❌ Error: "ModuleNotFoundError: No module named 'streamlit'"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r ../requirements.txt
```

### ❌ GitHub Actions falla

**Verifica**:
1. ✅ FRED_API_KEY está en GitHub Secrets
2. ✅ El nombre es exactamente `FRED_API_KEY`
3. ✅ La key es válida (pruébala localmente)

---

## 📖 Próximos Pasos

- 📚 Lee el [README completo](README.md) para entender las fórmulas
- 🎨 Personaliza tickers en `src/config.py`
- 🤖 Configura GitHub Actions para auto-actualización
- 📊 Exporta gráficos para presentaciones

---

## 🎯 Casos de Uso Rápidos

### Para procesos de selección en banca
```
"He creado un dashboard que monitorea liquidez global en tiempo real,
con actualización automática diaria via GitHub Actions.

Usa APIs de la Fed (FRED) y mercados (yfinance), calcula un índice
compuesto de liquidez con z-scores normalizados, y genera señales
de trading basadas en regímenes históricos.

Todo el código está en Python (pandas, streamlit, plotly) y
desplegado con CI/CD en GitHub."
```

### Para trading/análisis
- Verifica régimen actual: Crisis / Normal / Expansion
- Compara liquidez vs S&P 500 (correlación alta = 0.7+)
- Identifica inflexiones en Fed Balance Sheet
- Monitorea TGA + RRP para calcular liquidez neta

---

## 📞 ¿Necesitas ayuda?

- 📖 [README completo](README.md)
- 🐛 Abre un issue en GitHub
- 💬 Contacta al equipo

---

**¡Disfruta del dashboard! 🌍📊**
