"""
Módulo para descargar datos de FRED (Federal Reserve Economic Data).

Proporciona funciones para obtener series económicas de la Reserva Federal
que son fundamentales para el análisis de liquidez global.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from .config import FRED_API_KEY, FRED_SERIES, START_DATE, FRED_FREQUENCY

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_series(
    series_id: str,
    start_date: str = START_DATE,
    frequency: str = FRED_FREQUENCY,
    api_key: Optional[str] = None
) -> pd.Series:
    """
    Descarga una serie de datos de FRED.

    Args:
        series_id: ID de la serie de FRED (ej: 'WALCL')
        start_date: Fecha de inicio en formato 'YYYY-MM-DD'
        frequency: Frecuencia de datos ('d' diario, 'w' semanal, 'm' mensual)
        api_key: API key de FRED (si no se proporciona, usa FRED_API_KEY de config)

    Returns:
        pd.Series: Serie temporal con los datos, indexada por fecha

    Raises:
        ValueError: Si no hay API key configurada
        requests.HTTPError: Si hay error en la petición HTTP
    """
    key = api_key or FRED_API_KEY

    if not key:
        raise ValueError(
            "FRED_API_KEY no configurada. "
            "Obtén una key gratuita en: https://fred.stlouisfed.org/docs/api/api_key.html "
            "y configúrala como variable de entorno: export FRED_API_KEY='tu_key'"
        )

    params = {
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
        "frequency": frequency,
        "observation_start": start_date
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "observations" not in data:
            raise ValueError(f"No se encontraron observaciones para la serie {series_id}")

        observations = data["observations"]
        df = pd.DataFrame(observations)

        # Convertir a formato apropiado
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        # Crear serie temporal
        series = df.set_index("date")["value"]
        series.name = series_id

        return series

    except requests.exceptions.RequestException as e:
        raise requests.HTTPError(f"Error al descargar serie {series_id}: {str(e)}")


def fetch_all_fred_series(
    start_date: str = START_DATE,
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Descarga todas las series de FRED definidas en config.FRED_SERIES.

    Args:
        start_date: Fecha de inicio en formato 'YYYY-MM-DD'
        api_key: API key de FRED (opcional)

    Returns:
        pd.DataFrame: DataFrame con todas las series, indexado por fecha
    """
    series_dict = {}
    errors = []

    print(f"\n📊 Descargando {len(FRED_SERIES)} series de FRED...")

    for name, series_id in FRED_SERIES.items():
        try:
            print(f"  → {name} ({series_id})...", end=" ")
            series = fetch_fred_series(series_id, start_date=start_date, api_key=api_key)
            series_dict[name] = series
            print(f"✅ {len(series)} observaciones")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            errors.append((name, str(e)))

    if not series_dict:
        raise ValueError("No se pudo descargar ninguna serie de FRED")

    # Combinar todas las series en un DataFrame
    df = pd.DataFrame(series_dict)

    print(f"\n✅ Descarga completada: {len(df)} fechas, {len(df.columns)} series")

    if errors:
        print(f"\n⚠️  {len(errors)} series con errores:")
        for name, error in errors:
            print(f"  - {name}: {error}")

    return df


def calculate_net_liquidity(fred_df: pd.DataFrame) -> pd.Series:
    """
    Calcula la liquidez neta según la fórmula estándar:
    Net Liquidity = Fed Balance Sheet - TGA - Reverse Repo

    Args:
        fred_df: DataFrame con las series de FRED

    Returns:
        pd.Series: Serie temporal de liquidez neta
    """
    required_cols = ["fed_total_assets", "tga", "reverse_repo"]

    if not all(col in fred_df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in fred_df.columns]
        raise ValueError(f"Faltan columnas requeridas para calcular liquidez neta: {missing}")

    # Fórmula: Fed Assets - TGA - Reverse Repo
    net_liquidity = (
        fred_df["fed_total_assets"]
        - fred_df["tga"]
        - fred_df["reverse_repo"]
    )

    net_liquidity.name = "net_liquidity"
    return net_liquidity


if __name__ == "__main__":
    # Test básico
    try:
        df = fetch_all_fred_series()
        print("\n📈 Primeras 5 filas:")
        print(df.head())

        print("\n📈 Últimas 5 filas:")
        print(df.tail())

        # Calcular liquidez neta
        net_liq = calculate_net_liquidity(df)
        print(f"\n💧 Liquidez Neta - Último valor: ${net_liq.iloc[-1]:,.0f}M")

    except Exception as e:
        print(f"\n❌ Error en test: {str(e)}")
