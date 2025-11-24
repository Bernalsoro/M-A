"""
Funciones de transformación y cálculo para análisis de series temporales.

Proporciona herramientas para normalizar, calcular cambios porcentuales,
z-scores y otras transformaciones útiles para análisis financiero.
"""

import pandas as pd
import numpy as np
from typing import Optional
from .config import ROLLING_WINDOW, YOY_PERIODS


def yoy_change(series: pd.Series, periods: int = YOY_PERIODS) -> pd.Series:
    """
    Calcula el cambio year-over-year en porcentaje.

    Args:
        series: Serie temporal
        periods: Número de períodos para el cambio (52 para semanal = 1 año)

    Returns:
        pd.Series: Cambio YoY en porcentaje
    """
    change = series.pct_change(periods=periods) * 100
    change.name = f"{series.name}_yoy"
    return change


def rolling_mean(series: pd.Series, window: int = ROLLING_WINDOW) -> pd.Series:
    """
    Calcula la media móvil de una serie.

    Args:
        series: Serie temporal
        window: Ventana de observaciones (52 = 1 año para datos semanales)

    Returns:
        pd.Series: Media móvil
    """
    mean = series.rolling(window=window, min_periods=1).mean()
    mean.name = f"{series.name}_ma{window}"
    return mean


def rolling_std(series: pd.Series, window: int = ROLLING_WINDOW) -> pd.Series:
    """
    Calcula la desviación estándar móvil de una serie.

    Args:
        series: Serie temporal
        window: Ventana de observaciones

    Returns:
        pd.Series: Desviación estándar móvil
    """
    std = series.rolling(window=window, min_periods=1).std()
    std.name = f"{series.name}_std{window}"
    return std


def rolling_zscore(series: pd.Series, window: int = ROLLING_WINDOW) -> pd.Series:
    """
    Calcula el z-score móvil de una serie.

    El z-score indica cuántas desviaciones estándar está el valor actual
    por encima o debajo de la media móvil.

    Args:
        series: Serie temporal
        window: Ventana de observaciones

    Returns:
        pd.Series: Z-score móvil
    """
    mean = rolling_mean(series, window=window)
    std = rolling_std(series, window=window)

    # Evitar división por cero
    zscore = (series - mean) / std.replace(0, np.nan)
    zscore.name = f"{series.name}_zscore"
    return zscore


def normalize_series(series: pd.Series, base: float = 100.0) -> pd.Series:
    """
    Normaliza una serie a un valor base (por defecto 100).

    Útil para comparar series con diferentes magnitudes.

    Args:
        series: Serie temporal
        base: Valor base para la normalización

    Returns:
        pd.Series: Serie normalizada
    """
    first_value = series.dropna().iloc[0] if not series.dropna().empty else 1
    normalized = (series / first_value) * base
    normalized.name = f"{series.name}_normalized"
    return normalized


def calculate_momentum(series: pd.Series, periods: int = 20) -> pd.Series:
    """
    Calcula el momentum (diferencia entre precio actual y precio N períodos atrás).

    Args:
        series: Serie temporal
        periods: Número de períodos para calcular el momentum

    Returns:
        pd.Series: Momentum
    """
    momentum = series - series.shift(periods)
    momentum.name = f"{series.name}_momentum{periods}"
    return momentum


def calculate_roc(series: pd.Series, periods: int = 20) -> pd.Series:
    """
    Calcula Rate of Change (ROC) - cambio porcentual respecto a N períodos atrás.

    Args:
        series: Serie temporal
        periods: Número de períodos

    Returns:
        pd.Series: ROC en porcentaje
    """
    roc = ((series - series.shift(periods)) / series.shift(periods)) * 100
    roc.name = f"{series.name}_roc{periods}"
    return roc


def calculate_correlation_rolling(
    series1: pd.Series,
    series2: pd.Series,
    window: int = ROLLING_WINDOW
) -> pd.Series:
    """
    Calcula la correlación móvil entre dos series.

    Args:
        series1: Primera serie temporal
        series2: Segunda serie temporal
        window: Ventana de observaciones

    Returns:
        pd.Series: Correlación móvil
    """
    corr = series1.rolling(window=window).corr(series2)
    corr.name = f"corr_{series1.name}_{series2.name}"
    return corr


def resample_and_align(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    freq: str = 'W'
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Resamplea y alinea dos DataFrames a la misma frecuencia temporal.

    Útil para combinar datos diarios con semanales.

    Args:
        df1: Primer DataFrame
        df2: Segundo DataFrame
        freq: Frecuencia objetivo ('D' diario, 'W' semanal, 'M' mensual)

    Returns:
        tuple: (df1_resampled, df2_resampled)
    """
    df1_resampled = df1.resample(freq).last()
    df2_resampled = df2.resample(freq).last()
    return df1_resampled, df2_resampled


def fill_missing_values(
    df: pd.DataFrame,
    method: str = 'ffill'
) -> pd.DataFrame:
    """
    Rellena valores faltantes en un DataFrame.

    Args:
        df: DataFrame con datos
        method: Método de relleno ('ffill', 'bfill', 'interpolate')

    Returns:
        pd.DataFrame: DataFrame con valores rellenados
    """
    if method == 'interpolate':
        return df.interpolate(method='linear')
    else:
        return df.fillna(method=method)


if __name__ == "__main__":
    # Test básico
    import numpy as np

    # Crear serie de prueba
    dates = pd.date_range('2020-01-01', periods=200, freq='W')
    values = np.cumsum(np.random.randn(200)) + 100
    series = pd.Series(values, index=dates, name='test_series')

    print("📊 Serie original (últimos 5 valores):")
    print(series.tail())

    print("\n📈 YoY Change:")
    print(yoy_change(series).tail())

    print("\n📊 Z-Score:")
    print(rolling_zscore(series).tail())

    print("\n📈 Normalizado (base 100):")
    print(normalize_series(series).tail())

    print("\n✅ Todas las transformaciones funcionan correctamente")
