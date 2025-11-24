"""
Módulo para descargar datos de mercado usando yfinance.

Proporciona funciones para obtener precios históricos de activos financieros
como índices bursátiles, materias primas y criptomonedas.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional
from config import MARKET_TICKERS, YFINANCE_PERIOD, YFINANCE_INTERVAL


def fetch_ticker_data(
    ticker: str,
    period: str = YFINANCE_PERIOD,
    interval: str = YFINANCE_INTERVAL
) -> pd.Series:
    """
    Descarga datos históricos de un ticker usando yfinance.

    Args:
        ticker: Símbolo del ticker (ej: '^GSPC', 'BTC-USD')
        period: Período de datos ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval: Intervalo de datos ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')

    Returns:
        pd.Series: Serie temporal con precios de cierre ajustados, indexada por fecha

    Raises:
        ValueError: Si no se pueden obtener datos para el ticker
    """
    try:
        # Descargar datos
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period, interval=interval)

        if df.empty:
            raise ValueError(f"No se encontraron datos para el ticker {ticker}")

        # Retornar serie de precios de cierre
        series = df["Close"]
        series.name = ticker

        return series

    except Exception as e:
        raise ValueError(f"Error al descargar {ticker}: {str(e)}")


def fetch_market_prices(
    period: str = YFINANCE_PERIOD,
    interval: str = YFINANCE_INTERVAL
) -> pd.DataFrame:
    """
    Descarga precios de todos los tickers definidos en config.MARKET_TICKERS.

    Args:
        period: Período de datos
        interval: Intervalo de datos

    Returns:
        pd.DataFrame: DataFrame con precios de cierre ajustados, indexado por fecha
    """
    prices_dict = {}
    errors = []

    print(f"\n📈 Descargando {len(MARKET_TICKERS)} tickers de mercado...")

    for name, ticker in MARKET_TICKERS.items():
        try:
            print(f"  → {name} ({ticker})...", end=" ")
            series = fetch_ticker_data(ticker, period=period, interval=interval)
            prices_dict[name] = series
            print(f"✅ {len(series)} observaciones")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            errors.append((name, str(e)))

    if not prices_dict:
        raise ValueError("No se pudo descargar ningún ticker de mercado")

    # Combinar todas las series en un DataFrame
    df = pd.DataFrame(prices_dict)
    df.index.name = "date"

    print(f"\n✅ Descarga completada: {len(df)} fechas, {len(df.columns)} activos")

    if errors:
        print(f"\n⚠️  {len(errors)} tickers con errores:")
        for name, error in errors:
            print(f"  - {name}: {error}")

    return df


def calculate_returns(prices_df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
    """
    Calcula retornos porcentuales para todas las series de precios.

    Args:
        prices_df: DataFrame con precios
        periods: Número de períodos para calcular el retorno (1 = retorno diario)

    Returns:
        pd.DataFrame: DataFrame con retornos porcentuales
    """
    returns = prices_df.pct_change(periods=periods) * 100
    return returns


def calculate_cumulative_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula retornos acumulados desde el inicio para cada activo.

    Args:
        prices_df: DataFrame con precios

    Returns:
        pd.DataFrame: DataFrame con retornos acumulados (base 100)
    """
    # Normalizar a base 100 al inicio
    first_prices = prices_df.iloc[0]
    cumulative_returns = (prices_df / first_prices) * 100
    return cumulative_returns


def resample_to_weekly(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Resamplea datos diarios a semanales (última observación de la semana).

    Args:
        prices_df: DataFrame con precios diarios

    Returns:
        pd.DataFrame: DataFrame con precios semanales
    """
    weekly = prices_df.resample('W').last()
    return weekly


if __name__ == "__main__":
    # Test básico
    try:
        df = fetch_market_prices(period="1y", interval="1d")

        print("\n📊 Primeras 5 filas:")
        print(df.head())

        print("\n📊 Últimas 5 filas:")
        print(df.tail())

        # Calcular retornos
        returns = calculate_returns(df)
        print("\n📈 Retorno último día:")
        print(returns.iloc[-1])

        # Retorno acumulado
        cum_returns = calculate_cumulative_returns(df)
        print("\n📈 Retorno acumulado desde inicio (%):")
        print(((cum_returns.iloc[-1] / cum_returns.iloc[0]) - 1) * 100)

    except Exception as e:
        print(f"\n❌ Error en test: {str(e)}")
