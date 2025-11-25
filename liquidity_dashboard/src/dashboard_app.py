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
    """Crea gráfico dual de liquidez y S&P 500."""

    try:
        # Verificar que existan las columnas necesarias
        if 'liquidity_index' not in liquidity_df.columns:
            st.warning("⚠️ Columna 'liquidity_index' no encontrada")
            return None
        if 'sp500' not in market_df.columns:
            st.warning("⚠️ Columna 'sp500' no encontrada en datos de mercado")
            st.write("Columnas disponibles:", list(market_df.columns))
            return None

        # Verificar que hay datos
        if liquidity_df.empty or market_df.empty:
            st.warning("⚠️ Uno de los DataFrames está vacío")
            return None

        # Obtener series
        liq_series = liquidity_df['liquidity_index'].dropna()
        sp500_series = market_df['sp500'].dropna()

        if liq_series.empty or sp500_series.empty:
            st.warning("⚠️ Una de las series está vacía después de dropna()")
            return None

        # Crear DataFrame combinado ANTES de normalizar
        df_combined = pd.DataFrame({
            'liquidity_raw': liq_series,
            'sp500_raw': sp500_series
        })

        # Forward fill para manejar diferentes frecuencias
        df_combined = df_combined.fillna(method='ffill').fillna(method='bfill')

        # Eliminar filas donde AMBAS sean NaN
        df_combined = df_combined.dropna()

        if df_combined.empty:
            st.warning("⚠️ No hay datos superpuestos entre liquidez y S&P 500")
            st.write(f"📅 Rango liquidity: {liq_series.index.min()} a {liq_series.index.max()} ({len(liq_series)} puntos)")
            st.write(f"📅 Rango market: {sp500_series.index.min()} a {sp500_series.index.max()} ({len(sp500_series)} puntos)")
            return None

        # Normalizar las series combinadas
        liq_normalized = normalize_series(df_combined['liquidity_raw'])
        sp500_normalized = normalize_series(df_combined['sp500_raw'])

        # Crear DataFrame final
        df = pd.DataFrame({
            'liquidity': liq_normalized,
            'sp500': sp500_normalized
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

        # S&P 500
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['sp500'],
                name="S&P 500",
                line=dict(color='#ff7f0e', width=2),
            )
        )

        fig.update_layout(
            title="Global Liquidity vs S&P 500 (Normalized)",
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
            This dashboard tracks global liquidity conditions
            using Federal Reserve data and market indicators.

            **Liquidity Index**: Composite z-score of Fed assets,
            bank reserves, and M2 money supply.

            **Data Sources**:
            - FRED (Federal Reserve Economic Data)
            - Yahoo Finance (Market prices)
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
        chart = create_liquidity_chart(liquidity, market_weekly)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("⚠️ Liquidity chart not available")

    with tab2:
        chart = create_components_chart(liquidity)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("⚠️ Components chart not available")

    with tab3:
        regime_chart = create_regime_chart(liquidity)
        if regime_chart:
            st.plotly_chart(regime_chart, use_container_width=True)
        else:
            st.info("⚠️ Regime data not available")

    with tab4:
        # Mostrar todos los activos del mercado
        st.subheader("Market Prices (Normalized)")

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
