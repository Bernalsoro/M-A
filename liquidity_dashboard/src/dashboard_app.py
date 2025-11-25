"""
Global Liquidity Dashboard - Streamlit App

Dashboard interactivo para visualizar liquidez global y su relación
con los mercados financieros.
"""

import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

# Configurar el path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from transform import normalize_series

# Configuración de la página
st.set_page_config(
    page_title="Global Liquidity Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rutas de datos
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_RAW = BASE_DIR / "data" / "raw"


def ensure_data_exists():
    """Verifica si los datos existen, si no, los genera automáticamente."""
    liquidity_file = DATA_PROCESSED / "liquidity_data.csv"

    if not liquidity_file.exists():
        st.info("🔄 Primera carga: generando datos... Esto tomará 2-3 minutos.")

        # Crear directorios si no existen
        DATA_RAW.mkdir(parents=True, exist_ok=True)
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

        with st.spinner("Descargando datos de FRED y mercados..."):
            try:
                # Importar funciones de actualización
                from fetch_fred import fetch_all_fred_series, calculate_net_liquidity
                from fetch_market import fetch_market_prices, resample_to_weekly
                from indicators import build_liquidity_index, generate_liquidity_signals, calculate_liquidity_regime
                from config import START_DATE, YFINANCE_PERIOD, YFINANCE_INTERVAL

                # Descargar datos de FRED
                fred_df = fetch_all_fred_series(start_date=START_DATE)
                fred_df.to_csv(DATA_RAW / "fred_series.csv")

                # Descargar precios de mercado
                market_df = fetch_market_prices(period=YFINANCE_PERIOD, interval=YFINANCE_INTERVAL)
                market_df.to_csv(DATA_RAW / "market_prices.csv")

                # Calcular liquidez neta
                try:
                    net_liquidity = calculate_net_liquidity(fred_df)
                    fred_df['net_liquidity'] = net_liquidity
                except Exception as e:
                    st.warning(f"No se pudo calcular liquidez neta: {str(e)}")

                # Construir índice de liquidez
                liquidity_index = build_liquidity_index(fred_df)
                fred_df['liquidity_index'] = liquidity_index

                # Generar señales y régimen
                signals = generate_liquidity_signals(liquidity_index)
                regime = calculate_liquidity_regime(liquidity_index)
                fred_df['liquidity_signal'] = signals
                fred_df['liquidity_regime'] = regime

                # Resamplear market data a semanal
                market_weekly = resample_to_weekly(market_df)

                # Guardar datos procesados
                fred_df.to_csv(DATA_PROCESSED / "liquidity_data.csv")
                market_df.to_csv(DATA_PROCESSED / "market_prices.csv")
                market_weekly.to_csv(DATA_PROCESSED / "market_prices_weekly.csv")

                # Crear resumen
                summary = {
                    "metric": ["Última fecha (FRED)", "Última fecha (Market)", "Fed Assets (última)",
                              "Liquidity Index (z-score)", "Régimen"],
                    "value": [
                        fred_df.index[-1].strftime("%Y-%m-%d"),
                        market_df.index[-1].strftime("%Y-%m-%d"),
                        f"${fred_df['fed_total_assets'].iloc[-1]:,.0f}M",
                        f"{liquidity_index.iloc[-1]:.2f}",
                        regime.iloc[-1],
                    ]
                }
                summary_df = pd.DataFrame(summary)
                summary_df.to_csv(DATA_PROCESSED / "summary.csv", index=False)

                st.success("✅ Datos generados exitosamente!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error generando datos: {str(e)}")
                st.stop()


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data():
    """Carga los datos procesados."""
    # Asegurar que los datos existan
    ensure_data_exists()

    try:
        liquidity = pd.read_csv(
            DATA_PROCESSED / "liquidity_data.csv",
            parse_dates=["date"],
            index_col="date"
        )

        market_daily = pd.read_csv(
            DATA_PROCESSED / "market_prices.csv",
            parse_dates=["date"],
            index_col="date"
        )

        market_weekly = pd.read_csv(
            DATA_PROCESSED / "market_prices_weekly.csv",
            parse_dates=["date"],
            index_col="date"
        )

        # Remover timezone info de los índices para evitar conflictos
        if hasattr(liquidity.index, 'tz') and liquidity.index.tz is not None:
            liquidity.index = liquidity.index.tz_localize(None)
        if hasattr(market_daily.index, 'tz') and market_daily.index.tz is not None:
            market_daily.index = market_daily.index.tz_localize(None)
        if hasattr(market_weekly.index, 'tz') and market_weekly.index.tz is not None:
            market_weekly.index = market_weekly.index.tz_localize(None)

        summary = pd.read_csv(DATA_PROCESSED / "summary.csv")

        return liquidity, market_daily, market_weekly, summary

    except FileNotFoundError:
        st.error(
            "❌ Error cargando datos."
        )
        st.stop()


def create_liquidity_chart(liquidity_df: pd.DataFrame, market_df: pd.DataFrame):
    """Crea gráfico dual de liquidez y mercado de valores."""

    try:
        # Verificar que existan las columnas necesarias
        if 'liquidity_index' not in liquidity_df.columns:
            st.warning("⚠️ Columna 'liquidity_index' no encontrada")
            return None

        # Verificar que hay datos
        if liquidity_df.empty or market_df.empty:
            st.warning("⚠️ Uno de los DataFrames está vacío")
            return None

        # Determinar qué ticker de mercado usar (con fallback)
        market_ticker = None
        market_name = None

        # Intentar en orden de preferencia
        preference_order = ['sp500', 'nasdaq', 'gold', 'dxy']
        for ticker in preference_order:
            if ticker in market_df.columns:
                market_ticker = ticker
                market_name = {
                    'sp500': 'S&P 500',
                    'nasdaq': 'NASDAQ',
                    'gold': 'Gold',
                    'dxy': 'DXY'
                }.get(ticker, ticker.upper())
                break

        # Si no encontramos ninguno de los preferidos, usar el primero disponible
        if market_ticker is None and len(market_df.columns) > 0:
            market_ticker = market_df.columns[0]
            market_name = market_ticker.upper().replace('_', ' ')

        if market_ticker is None:
            st.warning("⚠️ No hay datos de mercado disponibles")
            st.write("Columnas en market_df:", list(market_df.columns))
            return None

        # Obtener series
        liq_series = liquidity_df['liquidity_index'].dropna()
        market_series = market_df[market_ticker].dropna()

        if liq_series.empty or market_series.empty:
            st.warning("⚠️ Una de las series está vacía después de dropna()")
            return None

        # Crear DataFrame combinado ANTES de normalizar
        df_combined = pd.DataFrame({
            'liquidity_raw': liq_series,
            'market_raw': market_series
        })

        # Forward fill para manejar diferentes frecuencias
        df_combined = df_combined.fillna(method='ffill').fillna(method='bfill')

        # Eliminar filas donde AMBAS sean NaN
        df_combined = df_combined.dropna()

        if df_combined.empty:
            st.warning(f"⚠️ No hay datos superpuestos entre liquidez y {market_name}")
            st.write(f"📅 Rango liquidity: {liq_series.index.min()} a {liq_series.index.max()} ({len(liq_series)} puntos)")
            st.write(f"📅 Rango market: {market_series.index.min()} a {market_series.index.max()} ({len(market_series)} puntos)")
            return None

        # Normalizar las series combinadas
        liq_normalized = normalize_series(df_combined['liquidity_raw'])
        market_normalized = normalize_series(df_combined['market_raw'])

        # Crear DataFrame final
        df = pd.DataFrame({
            'liquidity': liq_normalized,
            'market': market_normalized
        })

        fig = make_subplots(specs=[[{"secondary_y": False}]])

        # Liquidez
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['liquidity'],
                name="Liquidity Index",
                line=dict(color='#1f77b4', width=2),
            )
        )

        # Market ticker (dinámico)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['market'],
                name=market_name,
                line=dict(color='#ff7f0e', width=2),
            )
        )

        fig.update_layout(
            title=f"Global Liquidity vs {market_name} (Normalized)",
            xaxis_title="Date",
            yaxis_title="Normalized Value (Base 100)",
            hovermode='x unified',
            height=500,
            template="plotly_white"
        )

        return fig
    except Exception as e:
        st.error(f"Error creating liquidity chart: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None


def create_components_chart(liquidity_df: pd.DataFrame):
    """Crea gráfico de componentes de liquidez."""

    try:
        components = ['fed_total_assets', 'bank_reserves', 'm2']
        available = [col for col in components if col in liquidity_df.columns]

        if not available:
            st.warning("⚠️ No se encontraron componentes de liquidez")
            return None

        # Crear selectores para componentes
        col1, col2 = st.columns(2)

        with col1:
            show_m2 = st.checkbox("Incluir M2", value=False,
                                 help="M2 tiene un rango muy diferente, puede distorsionar la visualización")
        with col2:
            use_log = st.checkbox("Escala logarítmica", value=False,
                                 help="Útil para comparar series con diferentes magnitudes")

        # Determinar qué mostrar
        components_to_show = []
        for comp in available:
            if comp == 'm2' and not show_m2:
                continue
            components_to_show.append(comp)

        if not components_to_show:
            st.info("⚠️ Selecciona al menos un componente para visualizar")
            return None

        # Colores mejorados
        colors = {
            'fed_total_assets': '#1f77b4',  # Azul
            'bank_reserves': '#ff7f0e',     # Naranja
            'm2': '#2ca02c',                # Verde
            'tga': '#d62728',               # Rojo
            'reverse_repo': '#9467bd'       # Púrpura
        }

        fig = go.Figure()

        for component in components_to_show:
            data = liquidity_df[component].dropna()
            if not data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data,
                        name=component.replace('_', ' ').title(),
                        mode='lines',
                        line=dict(
                            color=colors.get(component, None),
                            width=2
                        )
                    )
                )

        fig.update_layout(
            title="Fed Balance Sheet Components",
            xaxis_title="Date",
            yaxis_title="Millions USD",
            yaxis_type='log' if use_log else 'linear',
            hovermode='x unified',
            height=400,
            template="plotly_white",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return fig
    except Exception as e:
        st.error(f"Error creating components chart: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None


def create_regime_chart(liquidity_df: pd.DataFrame):
    """Crea gráfico de régimen de liquidez."""

    try:
        if 'liquidity_regime' not in liquidity_df.columns or 'liquidity_index' not in liquidity_df.columns:
            return None

        # Mapear régimen a colores
        regime_colors = {
            'Crisis': '#d62728',
            'Contraction': '#ff7f0e',
            'Normal': '#2ca02c',
            'Expansion': '#1f77b4',
            'Extreme Expansion': '#9467bd'
        }

        df = liquidity_df[['liquidity_index', 'liquidity_regime']].dropna()

        if df.empty:
            st.warning("⚠️ No hay datos de régimen de liquidez")
            return None

        fig = go.Figure()

        for regime, color in regime_colors.items():
            mask = df['liquidity_regime'] == regime
            if mask.any():
                fig.add_trace(
                    go.Scatter(
                        x=df.index[mask],
                        y=df['liquidity_index'][mask],
                        name=regime,
                        mode='markers',
                        marker=dict(color=color, size=4)
                    )
                )

        fig.update_layout(
            title="Liquidity Regime Over Time",
            xaxis_title="Date",
            yaxis_title="Liquidity Index (Z-Score)",
            hovermode='x unified',
            height=400,
            template="plotly_white"
        )

        return fig
    except Exception as e:
        st.error(f"Error creating regime chart: {str(e)}")
        return None


def main():
    """Función principal del dashboard."""

    # Título
    st.title("🌍 Global Liquidity Dashboard")
    st.markdown("---")

    # Cargar datos
    with st.spinner("Loading data..."):
        liquidity, market_daily, market_weekly, summary = load_data()

    # Sidebar
    with st.sidebar:
        st.header("📊 Filters")

        # Selector de rango de fechas
        min_date = liquidity.index.min().date()
        max_date = liquidity.index.max().date()

        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown(
            """
            ### 🌍 Global Liquidity Dashboard

            Este dashboard monitorea las **condiciones de liquidez global**
            y su impacto en los mercados financieros.

            ### 🎯 ¿Por qué es importante?

            La liquidez de los bancos centrales (especialmente la Fed) es
            uno de los **drivers principales** de los mercados:

            - 📈 **Más liquidez** → Activos suben (acciones, cripto, oro)
            - 📉 **Menos liquidez** → Activos bajan (correcciones, bear markets)

            ### 🔢 ¿Qué mide el Liquidity Index?

            Índice compuesto (z-score) que combina:
            1. **Fed Total Assets** (Balance de la Reserva Federal)
            2. **Bank Reserves** (Reservas en bancos comerciales)
            3. **M2 Money Supply** (Oferta monetaria total)

            ### 📊 Fuentes de Datos

            - **FRED** (Federal Reserve Economic Data)
              - Datos oficiales de la Fed
              - Actualización semanal
            - **Yahoo Finance**
              - Precios de mercado (S&P 500, Bitcoin, oro, etc.)
              - Actualización diaria

            ### 🔄 Actualización

            Los datos se actualizan **automáticamente cada día**
            a las 02:00 UTC via GitHub Actions.

            ### 💡 Cómo usar este dashboard

            1. **Key Metrics**: Ve el régimen actual de liquidez
            2. **Liquidity vs Market**: Compara liquidez con mercado
            3. **Fed Components**: Analiza componentes del balance
            4. **Liquidity Regime**: Identifica el régimen histórico
            5. **Market Overview**: Compara diferentes activos

            **Cada gráfico tiene un botón** ℹ️ con explicaciones detalladas.
            """
        )

    # Filtrar por fechas
    if len(date_range) == 2:
        start_date, end_date = date_range
        # Convertir a string para evitar problemas con timezone
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        liquidity = liquidity.loc[start_str:end_str]
        market_weekly = market_weekly.loc[start_str:end_str]

    # Verificar que hay datos después del filtrado
    if liquidity.empty:
        st.warning("⚠️ No hay datos para el rango de fechas seleccionado")
        st.stop()

    # Métricas principales
    st.header("📈 Key Metrics")

    cols = st.columns(4)

    # Última actualización
    if len(liquidity) > 0:
        last_update = liquidity.index[-1].strftime("%Y-%m-%d")
        cols[0].metric("Last Update", last_update)

    # Liquidez neta
    if 'net_liquidity' in liquidity.columns and len(liquidity) > 0:
        net_liq_series = liquidity['net_liquidity'].dropna()
        if len(net_liq_series) > 0:
            net_liq = net_liq_series.iloc[-1]
            net_liq_prev = net_liq_series.iloc[-30] if len(net_liq_series) > 30 else net_liq_series.iloc[0]
            net_liq_delta = net_liq - net_liq_prev
            cols[1].metric(
                "Net Liquidity",
                f"${net_liq:,.0f}M",
                f"{net_liq_delta:,.0f}M"
            )

    # Índice de liquidez
    if 'liquidity_index' in liquidity.columns and len(liquidity) > 0:
        liq_index_series = liquidity['liquidity_index'].dropna()
        if len(liq_index_series) > 0:
            liq_index = liq_index_series.iloc[-1]
            liq_index_prev = liq_index_series.iloc[-30] if len(liq_index_series) > 30 else liq_index_series.iloc[0]
            liq_index_delta = liq_index - liq_index_prev
            cols[2].metric(
                "Liquidity Index",
                f"{liq_index:.2f}",
                f"{liq_index_delta:+.2f}"
            )

    # Régimen
    if 'liquidity_regime' in liquidity.columns and len(liquidity) > 0:
        regime_series = liquidity['liquidity_regime'].dropna()
        if len(regime_series) > 0:
            regime = regime_series.iloc[-1]
            cols[3].metric("Regime", regime)

    st.markdown("---")

    # Gráficos principales
    st.header("📊 Charts")

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs([
        "Liquidity vs Market",
        "Fed Components",
        "Liquidity Regime",
        "Market Overview"
    ])

    with tab1:
        # Explicación del gráfico
        with st.expander("ℹ️ Cómo interpretar este gráfico"):
            st.markdown("""
            ### 📊 ¿Qué muestra este gráfico?

            Compara la **liquidez global** con el rendimiento del **mercado de valores** (S&P 500, NASDAQ, o el índice disponible).

            ### 🔢 ¿Cómo se calcula?

            **Índice de Liquidez (línea azul)**:
            - Combina 3 métricas clave de la Reserva Federal:
              1. **Total de activos de la Fed** (Balance Sheet)
              2. **Reservas bancarias** (dinero que los bancos tienen en la Fed)
              3. **M2** (oferta monetaria total en la economía)
            - Cada métrica se convierte a **z-score** (cuántas desviaciones estándar está de su promedio)
            - Se promedian los 3 z-scores para crear el índice compuesto

            **Mercado (línea naranja/verde/dorada)**:
            - Precio de cierre del índice bursátil (descargado de Yahoo Finance)
            - Resampleado a frecuencia semanal para alinearse con datos de la Fed

            **Normalización**:
            - Ambas series se normalizan a base 100 en la fecha inicial
            - Esto permite compararlas visualmente en la misma escala
            - Valor 150 = creció 50% desde el inicio
            - Valor 80 = cayó 20% desde el inicio

            ### 💡 ¿Cómo interpretarlo?

            - **Líneas que suben juntas**: Mayor liquidez impulsa el mercado ✅
            - **Liquidez sube, mercado baja**: Anomalía temporal (crisis, pánico) ⚠️
            - **Liquidez baja, mercado sube**: Mercado sobreextendido, posible corrección 🔴
            - **Ambas caen**: Contracción de liquidez = presión bajista en mercados 📉

            **Regla general**: La liquidez tiende a liderar al mercado con 2-8 semanas de adelanto.
            """)

        chart = create_liquidity_chart(liquidity, market_weekly)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("⚠️ Liquidity chart not available")

    with tab2:
        # Explicación del gráfico
        with st.expander("ℹ️ Cómo interpretar este gráfico"):
            st.markdown("""
            ### 📊 ¿Qué muestra este gráfico?

            Muestra los **componentes individuales** del balance de la Reserva Federal que afectan la liquidez del sistema financiero.

            ### 🔢 ¿Cómo se obtiene la información?

            Todos los datos provienen de **FRED** (Federal Reserve Economic Data), la base de datos oficial de la Reserva Federal:

            **1. Fed Total Assets (WALCL)** - Azul
            - Total de activos en el balance de la Fed
            - Incluye: bonos del Tesoro, MBS (títulos respaldados por hipotecas), préstamos
            - **Fuente**: https://fred.stlouisfed.org/series/WALCL
            - **Frecuencia**: Semanal (miércoles)
            - **Unidad**: Millones de USD

            **2. Bank Reserves (WRESBAL)** - Naranja
            - Reservas que los bancos comerciales mantienen en la Fed
            - Dinero "estacionado" que los bancos pueden usar para préstamos
            - **Fuente**: https://fred.stlouisfed.org/series/WRESBAL
            - **Frecuencia**: Semanal (miércoles)
            - **Unidad**: Millones de USD

            **3. M2 Money Supply (WM2NS)** - Verde
            - Oferta monetaria total en la economía (efectivo + depósitos + fondos del mercado monetario)
            - Incluye: billetes, cuentas corrientes, cuentas de ahorro, fondos mutuos
            - **Fuente**: https://fred.stlouisfed.org/series/WM2NS
            - **Frecuencia**: Semanal (lunes)
            - **Unidad**: Miles de millones de USD (×1000)
            - ⚠️ **Nota**: M2 tiene una escala mucho mayor (~$21T) vs Fed Assets (~$8T), por eso está en checkbox separado

            ### 💡 ¿Cómo interpretarlo?

            **Fed Assets aumentan**:
            - La Fed está **comprando activos** (QE - Quantitative Easing)
            - Inyecta liquidez al sistema = **positivo para mercados** ✅

            **Bank Reserves aumentan**:
            - Los bancos tienen más dinero disponible para prestar
            - Mayor capacidad de crédito = **expansión económica** ✅

            **M2 aumenta**:
            - Hay más dinero circulando en la economía
            - Puede impulsar crecimiento pero también **inflación** ⚠️

            **Todos caen simultáneamente**:
            - Política monetaria restrictiva (QT - Quantitative Tightening)
            - Reducción de liquidez = **presión bajista en activos de riesgo** 🔴

            ### 🛠️ Opciones de visualización

            - **Incluir M2**: Actívalo para ver la oferta monetaria total (escala muy diferente)
            - **Escala logarítmica**: Útil para comparar tasas de cambio relativas cuando las magnitudes son muy diferentes
            """)

        chart = create_components_chart(liquidity)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("⚠️ Components chart not available")

    with tab3:
        # Explicación del gráfico
        with st.expander("ℹ️ Cómo interpretar este gráfico"):
            st.markdown("""
            ### 📊 ¿Qué muestra este gráfico?

            Clasifica cada periodo de tiempo en uno de **5 regímenes de liquidez** basándose en el índice de liquidez compuesto.

            ### 🔢 ¿Cómo se calcula?

            El **Liquidity Index** es un z-score que mide cuántas desviaciones estándar está la liquidez de su promedio histórico:

            - **Z-score = (valor actual - promedio móvil) / desviación estándar móvil**
            - Ventana rodante: 52 semanas (1 año)
            - Combina Fed Assets, Bank Reserves y M2

            **Clasificación de regímenes** (basada en el z-score):

            | Régimen | Z-Score | Color | Significado |
            |---------|---------|-------|-------------|
            | 🔴 **Crisis** | < -2.0 | Rojo | Liquidez extremadamente baja, crisis financiera |
            | 🟠 **Contraction** | -2.0 a -0.5 | Naranja | Contracción monetaria, Fed reduciendo balance |
            | 🟢 **Normal** | -0.5 a +0.5 | Verde | Condiciones normales, liquidez en rango histórico |
            | 🔵 **Expansion** | +0.5 a +2.0 | Azul | Expansión monetaria, Fed inyectando liquidez |
            | 🟣 **Extreme Expansion** | > +2.0 | Púrpura | QE extremo (como COVID-19, 2008) |

            ### 💡 ¿Cómo interpretarlo?

            **🔴 Crisis** (z < -2.0):
            - Ejemplo: Septiembre 2008 (Lehman Brothers)
            - Liquidez colapsando, pánico en mercados
            - **Acción**: La Fed típicamente interviene con QE masivo

            **🟠 Contraction** (-2.0 < z < -0.5):
            - La Fed está reduciendo su balance (QT)
            - Puede preceder correcciones en mercados
            - **Riesgo**: Activos de riesgo bajo presión

            **🟢 Normal** (-0.5 < z < +0.5):
            - Condiciones estándar, no hay estrés ni exceso
            - Mercados funcionando normalmente

            **🔵 Expansion** (+0.5 < z < +2.0):
            - QE activo, Fed comprando activos
            - **Positivo**: Impulso alcista para acciones, cripto, oro

            **🟣 Extreme Expansion** (z > +2.0):
            - QE extremo (COVID, 2008-2009)
            - **Muy alcista** a corto plazo
            - ⚠️ **Cuidado**: Puede generar burbujas y alta inflación futura

            ### 📈 Estrategia de Trading

            - **Crisis → Expansion**: Momento de comprar activos de riesgo (máximo potencial) 🚀
            - **Expansion → Normal**: Mantener posiciones, tomar ganancias parciales 📊
            - **Normal → Contraction**: Reducir exposición, aumentar efectivo 💰
            - **Contraction → Crisis**: Solo para traders experimentados, alta volatilidad ⚠️

            **Nota histórica**: Los mayores retornos del S&P 500 ocurren durante regímenes de **Expansion** y **Extreme Expansion**.
            """)

        regime_chart = create_regime_chart(liquidity)
        if regime_chart:
            st.plotly_chart(regime_chart, use_container_width=True)
        else:
            st.info("⚠️ Regime data not available")

    with tab4:
        # Mostrar todos los activos del mercado
        st.subheader("Market Prices (Normalized)")

        # Explicación del gráfico
        with st.expander("ℹ️ Cómo interpretar este gráfico"):
            st.markdown("""
            ### 📊 ¿Qué muestra este gráfico?

            Compara el rendimiento de **diferentes clases de activos** normalizados a base 100 para facilitar la comparación visual.

            ### 🔢 ¿Cómo se obtiene la información?

            Todos los precios provienen de **Yahoo Finance** (vía librería `yfinance`):

            **📈 Índices de Acciones**:
            - **S&P 500** (^GSPC): Índice de las 500 empresas más grandes de EEUU
            - **NASDAQ** (^IXIC): Índice tech-heavy, incluye Apple, Microsoft, Amazon, etc.

            **🏆 Commodities**:
            - **Gold** (GC=F): Oro, contratos futuros (safe haven tradicional)

            **💰 Cripto**:
            - **Bitcoin** (BTC-USD): Criptomoneda principal, altamente volátil
            - ⚠️ **Nota**: Bitcoin puede crecer 10x o caer 80% en un año, por eso está separado

            **💵 Divisas**:
            - **DXY** (DX-Y.NYB): Índice del Dólar estadounidense vs canasta de divisas (EUR, JPY, GBP, etc.)

            **📊 Bonos**:
            - **10-Year Treasury** (^TNX): Rendimiento del bono del Tesoro a 10 años (%)
            - Sube cuando los precios de bonos bajan (relación inversa)

            **Proceso de datos**:
            1. Descarga diaria de Yahoo Finance
            2. Resampleado a frecuencia **semanal** (último precio de la semana)
            3. **Normalización a base 100** en la fecha inicial del rango seleccionado

            ### 💡 ¿Cómo interpretarlo?

            **Normalización a Base 100**:
            - Si un activo está en **150**: Ha crecido **+50%** desde el inicio
            - Si un activo está en **80**: Ha caído **-20%** desde el inicio
            - Facilita comparar activos con precios muy diferentes (Bitcoin $60k vs Oro $2k)

            **Patrones típicos**:

            **🟢 Alta liquidez (QE activo)**:
            - S&P 500 ↗️ (sube)
            - NASDAQ ↗️↗️ (sube más que S&P)
            - Bitcoin ↗️↗️↗️ (máximo beneficiado)
            - Gold ↗️ (protección contra inflación)
            - DXY ↘️ (dólar débil por exceso de oferta)

            **🔴 Baja liquidez (QT activo)**:
            - S&P 500 ↘️ (baja)
            - NASDAQ ↘️↘️ (cae más que S&P)
            - Bitcoin ↘️↘️↘️ (máximo castigado)
            - Gold → o ↗️ (refugio seguro)
            - DXY ↗️ (dólar fuerte, flight to safety)

            **Correlaciones**:
            - **S&P 500 vs NASDAQ**: Alta correlación positiva (~0.9)
            - **S&P 500 vs DXY**: Correlación negativa (~-0.5 a -0.7)
            - **Bitcoin vs Liquidez**: Altamente sensible, beta >2
            - **Gold vs S&P 500**: Baja correlación, diversificación

            ### 🛠️ Opciones de visualización

            - **Incluir Bitcoin**: Actívalo para ver cripto (puede dominar el gráfico por su volatilidad extrema)
            - **Escala logarítmica**: Actívala cuando incluyas Bitcoin o cuando los rangos sean muy diferentes
              - En escala log, una línea recta = tasa de crecimiento constante
              - Útil para comparar % de cambio en vez de cambio absoluto

            ### 📊 Estadísticas de Performance

            Abajo del gráfico verás las métricas de cada activo:
            - **Valor actual** (normalizado): Dónde está ahora respecto al inicio
            - **Cambio %**: Ganancia o pérdida total en el periodo

            **Ejemplo**:
            - NASDAQ: 165.3 (+65.3%) → Creció 65% en el periodo
            - DXY: 95.2 (-4.8%) → Cayó 5% en el periodo
            """)

        try:
            if market_weekly.empty:
                st.warning("⚠️ No hay datos de mercado para mostrar")
            else:
                # Selector de activos a mostrar
                all_assets = list(market_weekly.columns)

                # Separar Bitcoin de los demás por su volatilidad extrema
                traditional_assets = [a for a in all_assets if a != 'bitcoin']

                col1, col2 = st.columns(2)
                with col1:
                    show_bitcoin = st.checkbox("Incluir Bitcoin", value=False,
                                              help="Bitcoin tiene un rango muy diferente, puede distorsionar la visualización")
                with col2:
                    use_log_scale = st.checkbox("Escala logarítmica", value=False,
                                               help="Útil cuando hay activos con rangos muy diferentes")

                # Determinar qué activos mostrar
                assets_to_show = traditional_assets.copy()
                if show_bitcoin and 'bitcoin' in all_assets:
                    assets_to_show.append('bitcoin')

                if not assets_to_show:
                    st.warning("⚠️ No hay activos seleccionados")
                else:
                    # Normalizar solo columnas seleccionadas
                    market_normalized = pd.DataFrame()
                    for col in assets_to_show:
                        if col in market_weekly.columns:
                            col_data = market_weekly[col].dropna()
                            if len(col_data) > 0:
                                market_normalized[col] = normalize_series(col_data)

                    if market_normalized.empty:
                        st.warning("⚠️ No se pudieron normalizar los datos de mercado")
                    else:
                        # Colores más distinguibles
                        colors = {
                            'sp500': '#1f77b4',      # Azul
                            'nasdaq': '#ff7f0e',     # Naranja
                            'gold': '#FFD700',       # Dorado
                            'bitcoin': '#F7931A',    # Bitcoin naranja
                            'dxy': '#2ca02c',        # Verde
                            'ten_year_treasury': '#d62728'  # Rojo
                        }

                        fig = go.Figure()
                        for col in market_normalized.columns:
                            fig.add_trace(
                                go.Scatter(
                                    x=market_normalized.index,
                                    y=market_normalized[col],
                                    name=col.upper().replace('_', ' '),
                                    mode='lines',
                                    line=dict(
                                        color=colors.get(col, None),
                                        width=2
                                    )
                                )
                            )

                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Normalized Value (Base 100)",
                            yaxis_type='log' if use_log_scale else 'linear',
                            hovermode='x unified',
                            height=500,
                            template="plotly_white",
                            legend=dict(
                                yanchor="top",
                                y=0.99,
                                xanchor="left",
                                x=0.01
                            )
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Mostrar estadísticas
                        if len(market_normalized.columns) > 0:
                            st.subheader("📊 Performance desde inicio del período")
                            perf_cols = st.columns(len(market_normalized.columns))
                            for idx, col in enumerate(market_normalized.columns):
                                latest = market_normalized[col].iloc[-1]
                                change = latest - 100
                                perf_cols[idx].metric(
                                    col.upper().replace('_', ' '),
                                    f"{latest:.1f}",
                                    f"{change:+.1f}%"
                                )
        except Exception as e:
            st.error(f"Error displaying market overview: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

    # Tabla de resumen
    st.markdown("---")
    st.header("📋 Summary Table")
    st.dataframe(summary, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption(
        f"Dashboard actualizado automáticamente. "
        f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
