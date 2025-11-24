"""
Indicadores de liquidez global y métricas derivadas.

Este módulo construye índices compuestos de liquidez basados en múltiples
series de datos de la Fed y otros indicadores económicos.
"""

import pandas as pd
import numpy as np
from typing import Optional, List
from .transform import rolling_zscore, normalize_series
from .config import ROLLING_WINDOW


def build_liquidity_index(
    fred_df: pd.DataFrame,
    components: Optional[List[str]] = None,
    window: int = ROLLING_WINDOW
) -> pd.Series:
    """
    Construye un índice de liquidez global basado en z-scores de componentes clave.

    El índice promedia los z-scores de diferentes medidas de liquidez para crear
    un indicador compuesto que refleja las condiciones de liquidez del sistema.

    Args:
        fred_df: DataFrame con series de FRED
        components: Lista de componentes a usar (si None, usa componentes por defecto)
        window: Ventana para cálculo de z-scores

    Returns:
        pd.Series: Índice de liquidez (promedio de z-scores)
    """
    # Componentes por defecto
    if components is None:
        components = ["fed_total_assets", "bank_reserves", "m2"]

    # Verificar que existan los componentes
    available_components = [col for col in components if col in fred_df.columns]

    if not available_components:
        raise ValueError(f"No se encontraron componentes válidos. Disponibles: {list(fred_df.columns)}")

    print(f"📊 Construyendo índice de liquidez con: {', '.join(available_components)}")

    # Calcular z-scores para cada componente
    zscores_dict = {}
    for component in available_components:
        zscore = rolling_zscore(fred_df[component], window=window)
        zscores_dict[component] = zscore

    # Crear DataFrame de z-scores
    zscores_df = pd.DataFrame(zscores_dict)

    # Calcular promedio de z-scores (índice de liquidez)
    liquidity_index = zscores_df.mean(axis=1)
    liquidity_index.name = "liquidity_index"

    return liquidity_index


def calculate_liquidity_momentum(
    liquidity_index: pd.Series,
    short_window: int = 13,
    long_window: int = 26
) -> pd.Series:
    """
    Calcula el momentum del índice de liquidez (diferencia entre MA corta y larga).

    Args:
        liquidity_index: Serie del índice de liquidez
        short_window: Ventana corta (13 semanas ≈ 3 meses)
        long_window: Ventana larga (26 semanas ≈ 6 meses)

    Returns:
        pd.Series: Momentum de liquidez
    """
    ma_short = liquidity_index.rolling(window=short_window).mean()
    ma_long = liquidity_index.rolling(window=long_window).mean()

    momentum = ma_short - ma_long
    momentum.name = "liquidity_momentum"

    return momentum


def generate_liquidity_signals(liquidity_index: pd.Series) -> pd.Series:
    """
    Genera señales de trading basadas en el índice de liquidez.

    Señales:
    - 1 (Buy): Liquidez en expansión (z-score > 0.5)
    - 0 (Neutral): Liquidez neutral (-0.5 <= z-score <= 0.5)
    - -1 (Sell): Liquidez en contracción (z-score < -0.5)

    Args:
        liquidity_index: Serie del índice de liquidez

    Returns:
        pd.Series: Señales de trading (-1, 0, 1)
    """
    signals = pd.Series(0, index=liquidity_index.index, name="liquidity_signal")

    signals[liquidity_index > 0.5] = 1    # Buy signal
    signals[liquidity_index < -0.5] = -1  # Sell signal

    return signals


def calculate_liquidity_regime(
    liquidity_index: pd.Series,
    thresholds: Optional[tuple] = None
) -> pd.Series:
    """
    Clasifica el régimen de liquidez en categorías.

    Regímenes:
    - "Crisis": z-score < -1.5
    - "Contraction": -1.5 <= z-score < -0.5
    - "Normal": -0.5 <= z-score <= 0.5
    - "Expansion": 0.5 < z-score <= 1.5
    - "Extreme Expansion": z-score > 1.5

    Args:
        liquidity_index: Serie del índice de liquidez
        thresholds: Tupla de umbrales (low, mid_low, mid_high, high)

    Returns:
        pd.Series: Régimen de liquidez (categórico)
    """
    if thresholds is None:
        thresholds = (-1.5, -0.5, 0.5, 1.5)

    t1, t2, t3, t4 = thresholds

    regime = pd.Series("Normal", index=liquidity_index.index, name="liquidity_regime")

    regime[liquidity_index < t1] = "Crisis"
    regime[(liquidity_index >= t1) & (liquidity_index < t2)] = "Contraction"
    regime[(liquidity_index > t3) & (liquidity_index <= t4)] = "Expansion"
    regime[liquidity_index > t4] = "Extreme Expansion"

    return regime


def calculate_liquidity_percentile(
    liquidity_index: pd.Series,
    window: Optional[int] = None
) -> pd.Series:
    """
    Calcula el percentil histórico del índice de liquidez.

    Args:
        liquidity_index: Serie del índice de liquidez
        window: Ventana para el cálculo (None = todo el histórico)

    Returns:
        pd.Series: Percentil histórico (0-100)
    """
    if window is None:
        # Percentil sobre todo el histórico
        percentile = liquidity_index.rank(pct=True) * 100
    else:
        # Percentil móvil
        percentile = liquidity_index.rolling(window=window).apply(
            lambda x: (x.rank(pct=True).iloc[-1]) * 100 if len(x) > 0 else np.nan
        )

    percentile.name = "liquidity_percentile"
    return percentile


def create_composite_indicator(
    liquidity_index: pd.Series,
    market_prices: pd.DataFrame,
    market_asset: str = "sp500"
) -> pd.DataFrame:
    """
    Crea un indicador compuesto que combina liquidez y precio de activo.

    Args:
        liquidity_index: Serie del índice de liquidez
        market_prices: DataFrame con precios de mercado
        market_asset: Nombre del activo a usar (por defecto S&P 500)

    Returns:
        pd.DataFrame: DataFrame con liquidez, precio normalizado y señal compuesta
    """
    # Normalizar el activo de mercado
    market_normalized = normalize_series(market_prices[market_asset])

    # Combinar en un DataFrame
    df = pd.DataFrame({
        'liquidity_index': liquidity_index,
        f'{market_asset}_normalized': market_normalized
    })

    # Alinear índices
    df = df.dropna()

    # Calcular correlación móvil
    df['correlation'] = df['liquidity_index'].rolling(window=52).corr(df[f'{market_asset}_normalized'])

    return df


if __name__ == "__main__":
    # Test básico con datos simulados
    import numpy as np

    dates = pd.date_range('2020-01-01', periods=200, freq='W')

    # Simular datos de Fed
    fred_data = pd.DataFrame({
        'fed_total_assets': np.cumsum(np.random.randn(200) * 100) + 5000,
        'bank_reserves': np.cumsum(np.random.randn(200) * 50) + 2000,
        'm2': np.cumsum(np.random.randn(200) * 80) + 15000,
    }, index=dates)

    print("📊 Construyendo índice de liquidez...")
    liq_index = build_liquidity_index(fred_data)

    print("\n📈 Últimos valores del índice:")
    print(liq_index.tail())

    print("\n📊 Régimen actual:")
    regime = calculate_liquidity_regime(liq_index)
    print(regime.tail())

    print("\n🎯 Señales de trading:")
    signals = generate_liquidity_signals(liq_index)
    print(signals.tail())

    print("\n✅ Indicadores construidos correctamente")
