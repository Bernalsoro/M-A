"""
Configuración para el Global Liquidity Dashboard.

Este módulo define las APIs, series de datos y tickers que se utilizan
para el análisis de liquidez global.
"""

import os

# Intentar importar streamlit para leer secrets (cuando está deployado)
try:
    import streamlit as st
    # Si estamos en Streamlit Cloud, usar secrets
    if hasattr(st, 'secrets') and 'FRED_API_KEY' in st.secrets:
        FRED_API_KEY = st.secrets['FRED_API_KEY']
    else:
        # Si no, usar variable de entorno
        FRED_API_KEY = os.getenv("FRED_API_KEY", "")
except (ImportError, FileNotFoundError):
    # Si streamlit no está disponible o no hay secrets, usar variable de entorno
    FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# Series de FRED (Federal Reserve Economic Data)
# Estas series representan los componentes clave de liquidez del sistema
FRED_SERIES = {
    "fed_total_assets": "WALCL",       # Total Assets of Federal Reserve
    "bank_reserves": "WRESBAL",        # Reserve Balances with Federal Reserve Banks
    "tga": "WTREGEN",                  # Treasury General Account
    "reverse_repo": "RRPONTSYD",       # Overnight Reverse Repurchase Agreements
    "m2": "WM2NS",                     # M2 Money Stock (weekly)
}

# Tickers de mercado (via yfinance)
MARKET_TICKERS = {
    "sp500": "^GSPC",                  # S&P 500 Index
    "nasdaq": "^IXIC",                 # NASDAQ Composite
    "gold": "GC=F",                    # Gold Futures
    "bitcoin": "BTC-USD",              # Bitcoin USD
    "dxy": "DX-Y.NYB",                 # US Dollar Index
    "ten_year_treasury": "^TNX",       # 10-Year Treasury Yield
}

# Configuración de fechas
START_DATE = "2008-01-01"  # Desde la crisis financiera para tener perspectiva histórica

# Configuración de frecuencia para FRED
FRED_FREQUENCY = "w"  # 'w' = weekly, 'd' = daily, 'm' = monthly

# Configuración de yfinance
YFINANCE_PERIOD = "15y"  # Período de descarga
YFINANCE_INTERVAL = "1d"  # Intervalo diario

# Parámetros para cálculos
ROLLING_WINDOW = 52  # Ventana de 52 semanas (1 año) para z-scores y medias móviles
YOY_PERIODS = 52     # 52 semanas para cambio year-over-year
