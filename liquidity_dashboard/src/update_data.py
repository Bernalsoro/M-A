"""
Script de actualización de datos para el Global Liquidity Dashboard.

Este script descarga los datos más recientes de FRED y mercados,
calcula indicadores derivados y guarda los resultados procesados.

Puede ejecutarse manualmente o programarse para ejecución automática
(cron, Task Scheduler, GitHub Actions).
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings

# Suprimir warnings de yfinance
warnings.filterwarnings('ignore')

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_fred import fetch_all_fred_series, calculate_net_liquidity
from fetch_market import fetch_market_prices, resample_to_weekly
from indicators import build_liquidity_index, generate_liquidity_signals, calculate_liquidity_regime
from config import START_DATE, YFINANCE_PERIOD, YFINANCE_INTERVAL


# Rutas de datos
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"


def ensure_directories():
    """Crea directorios de datos si no existen."""
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


def save_metadata(success: bool, error_msg: str = ""):
    """Guarda metadata de la última actualización."""
    metadata = {
        "last_update": datetime.now().isoformat(),
        "success": success,
        "error": error_msg
    }

    metadata_df = pd.DataFrame([metadata])
    metadata_df.to_csv(DATA_PROCESSED / "update_metadata.csv", index=False)


def main():
    """
    Función principal que ejecuta el pipeline de actualización completo.
    """
    print("=" * 70)
    print("🌍 GLOBAL LIQUIDITY DASHBOARD - DATA UPDATE")
    print("=" * 70)
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # 1. Asegurar que existen los directorios
        ensure_directories()

        # 2. Descargar datos de FRED
        print("📊 PASO 1: Descargando datos de FRED...")
        print("-" * 70)
        fred_df = fetch_all_fred_series(start_date=START_DATE)
        fred_df.to_csv(DATA_RAW / "fred_series.csv")
        print(f"✅ Guardado en: {DATA_RAW / 'fred_series.csv'}")
        print()

        # 3. Descargar precios de mercado
        print("📈 PASO 2: Descargando precios de mercado...")
        print("-" * 70)
        market_df = fetch_market_prices(period=YFINANCE_PERIOD, interval=YFINANCE_INTERVAL)
        market_df.to_csv(DATA_RAW / "market_prices.csv")
        print(f"✅ Guardado en: {DATA_RAW / 'market_prices.csv'}")
        print()

        # 4. Calcular liquidez neta
        print("💧 PASO 3: Calculando liquidez neta...")
        print("-" * 70)
        try:
            net_liquidity = calculate_net_liquidity(fred_df)
            fred_df['net_liquidity'] = net_liquidity
            print(f"✅ Liquidez neta calculada: ${net_liquidity.iloc[-1]:,.0f}M (último valor)")
        except Exception as e:
            print(f"⚠️  No se pudo calcular liquidez neta: {str(e)}")
        print()

        # 5. Construir índice de liquidez
        print("📊 PASO 4: Construyendo índice de liquidez...")
        print("-" * 70)
        liquidity_index = build_liquidity_index(fred_df)
        fred_df['liquidity_index'] = liquidity_index
        print(f"✅ Índice de liquidez: {liquidity_index.iloc[-1]:.2f} (último z-score)")
        print()

        # 6. Generar señales y régimen
        print("🎯 PASO 5: Generando señales de trading y régimen...")
        print("-" * 70)
        signals = generate_liquidity_signals(liquidity_index)
        regime = calculate_liquidity_regime(liquidity_index)
        fred_df['liquidity_signal'] = signals
        fred_df['liquidity_regime'] = regime

        last_signal = signals.iloc[-1]
        last_regime = regime.iloc[-1]
        signal_emoji = "🟢" if last_signal == 1 else "🔴" if last_signal == -1 else "🟡"
        print(f"✅ Señal actual: {signal_emoji} {last_signal}")
        print(f"✅ Régimen actual: {last_regime}")
        print()

        # 7. Resamplear market data a semanal para alinearlo con FRED
        print("📊 PASO 6: Alineando datos de mercado (resample a semanal)...")
        print("-" * 70)
        market_weekly = resample_to_weekly(market_df)
        print(f"✅ {len(market_df)} observaciones diarias → {len(market_weekly)} semanales")
        print()

        # 8. Guardar datos procesados
        print("💾 PASO 7: Guardando datos procesados...")
        print("-" * 70)

        # Guardar datos de liquidez procesados
        fred_df.to_csv(DATA_PROCESSED / "liquidity_data.csv")
        print(f"✅ {DATA_PROCESSED / 'liquidity_data.csv'}")

        # Guardar market data (diario)
        market_df.to_csv(DATA_PROCESSED / "market_prices.csv")
        print(f"✅ {DATA_PROCESSED / 'market_prices.csv'}")

        # Guardar market data (semanal)
        market_weekly.to_csv(DATA_PROCESSED / "market_prices_weekly.csv")
        print(f"✅ {DATA_PROCESSED / 'market_prices_weekly.csv'}")

        # 9. Crear archivo de resumen
        print()
        print("📋 PASO 8: Generando resumen...")
        print("-" * 70)

        summary = {
            "metric": [
                "Última fecha (FRED)",
                "Última fecha (Market)",
                "Fed Assets (última)",
                "Net Liquidity (última)",
                "Liquidity Index (z-score)",
                "Régimen",
                "Señal",
            ],
            "value": [
                fred_df.index[-1].strftime("%Y-%m-%d"),
                market_df.index[-1].strftime("%Y-%m-%d"),
                f"${fred_df['fed_total_assets'].iloc[-1]:,.0f}M",
                f"${net_liquidity.iloc[-1]:,.0f}M" if 'net_liquidity' in fred_df.columns else "N/A",
                f"{liquidity_index.iloc[-1]:.2f}",
                last_regime,
                f"{last_signal} {signal_emoji}",
            ]
        }

        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(DATA_PROCESSED / "summary.csv", index=False)
        print(summary_df.to_string(index=False))
        print()

        # 10. Guardar metadata de éxito
        save_metadata(success=True)

        print("=" * 70)
        print("✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO")
        print(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR EN LA ACTUALIZACIÓN")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print()

        import traceback
        traceback.print_exc()

        # Guardar metadata de error
        save_metadata(success=False, error_msg=str(e))

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
