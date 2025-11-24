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


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data():
    """Carga los datos procesados."""
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

        summary = pd.read_csv(DATA_PROCESSED / "summary.csv")

        return liquidity, market_daily, market_weekly, summary

    except FileNotFoundError:
        st.error(
            "❌ No se encontraron datos. Por favor ejecuta primero:\n"
            "`python src/update_data.py`"
        )
        st.stop()


def create_liquidity_chart(liquidity_df: pd.DataFrame, market_df: pd.DataFrame):
    """Crea gráfico dual de liquidez y S&P 500."""

    # Normalizar ambas series
    liq_normalized = normalize_series(liquidity_df['liquidity_index'])
    sp500_normalized = normalize_series(market_df['sp500'])

    # Alinear fechas
    df = pd.DataFrame({
        'liquidity': liq_normalized,
        'sp500': sp500_normalized
    }).dropna()

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


def create_components_chart(liquidity_df: pd.DataFrame):
    """Crea gráfico de componentes de liquidez."""

    components = ['fed_total_assets', 'bank_reserves', 'm2']
    available = [col for col in components if col in liquidity_df.columns]

    fig = go.Figure()

    for component in available:
        fig.add_trace(
            go.Scatter(
                x=liquidity_df.index,
                y=liquidity_df[component],
                name=component.replace('_', ' ').title(),
                mode='lines'
            )
        )

    fig.update_layout(
        title="Fed Balance Sheet Components",
        xaxis_title="Date",
        yaxis_title="Millions USD",
        hovermode='x unified',
        height=400,
        template="plotly_white"
    )

    return fig


def create_regime_chart(liquidity_df: pd.DataFrame):
    """Crea gráfico de régimen de liquidez."""

    if 'liquidity_regime' not in liquidity_df.columns:
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
        liquidity = liquidity.loc[start_date:end_date]
        market_weekly = market_weekly.loc[start_date:end_date]

    # Métricas principales
    st.header("📈 Key Metrics")

    cols = st.columns(4)

    # Última actualización
    last_update = liquidity.index[-1].strftime("%Y-%m-%d")
    cols[0].metric("Last Update", last_update)

    # Liquidez neta
    if 'net_liquidity' in liquidity.columns:
        net_liq = liquidity['net_liquidity'].iloc[-1]
        net_liq_prev = liquidity['net_liquidity'].iloc[-30] if len(liquidity) > 30 else liquidity['net_liquidity'].iloc[0]
        net_liq_delta = net_liq - net_liq_prev
        cols[1].metric(
            "Net Liquidity",
            f"${net_liq:,.0f}M",
            f"{net_liq_delta:,.0f}M"
        )

    # Índice de liquidez
    liq_index = liquidity['liquidity_index'].iloc[-1]
    liq_index_prev = liquidity['liquidity_index'].iloc[-30] if len(liquidity) > 30 else liquidity['liquidity_index'].iloc[0]
    liq_index_delta = liq_index - liq_index_prev
    cols[2].metric(
        "Liquidity Index",
        f"{liq_index:.2f}",
        f"{liq_index_delta:+.2f}"
    )

    # Régimen
    if 'liquidity_regime' in liquidity.columns:
        regime = liquidity['liquidity_regime'].iloc[-1]
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
        st.plotly_chart(
            create_liquidity_chart(liquidity, market_weekly),
            use_container_width=True
        )

    with tab2:
        st.plotly_chart(
            create_components_chart(liquidity),
            use_container_width=True
        )

    with tab3:
        regime_chart = create_regime_chart(liquidity)
        if regime_chart:
            st.plotly_chart(regime_chart, use_container_width=True)
        else:
            st.info("Regime data not available")

    with tab4:
        # Mostrar todos los activos del mercado
        st.subheader("Market Prices (Normalized)")

        market_normalized = market_weekly.apply(normalize_series)

        fig = go.Figure()
        for col in market_normalized.columns:
            fig.add_trace(
                go.Scatter(
                    x=market_normalized.index,
                    y=market_normalized[col],
                    name=col.upper(),
                    mode='lines'
                )
            )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Normalized Value (Base 100)",
            hovermode='x unified',
            height=500,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

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
