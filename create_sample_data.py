"""
Create Sample Historical Data for Backtesting
Since Binance API is blocked, we'll create realistic sample data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os


def generate_realistic_crypto_data(
    symbol: str,
    start_date: str,
    days: int,
    timeframe: str = '1h',
    base_price: float = 60000,
    trend_direction: str = 'up',  # 'up', 'down', 'sideways'
    volatility: float = 0.02
):
    """Generate realistic-looking crypto OHLCV data"""

    # Calculate intervals
    interval_minutes = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }

    minutes = interval_minutes.get(timeframe, 60)
    total_candles = int((days * 24 * 60) / minutes)

    # Generate timestamps
    start = datetime.strptime(start_date, '%Y-%m-%d')
    timestamps = [start + timedelta(minutes=minutes*i) for i in range(total_candles)]

    # Generate price series
    np.random.seed(42)  # For reproducibility

    # Base trend
    if trend_direction == 'up':
        trend = np.linspace(0, base_price * 0.15, total_candles)  # 15% uptrend
    elif trend_direction == 'down':
        trend = np.linspace(0, -base_price * 0.10, total_candles)  # 10% downtrend
    else:  # sideways
        trend = np.sin(np.linspace(0, 4*np.pi, total_candles)) * base_price * 0.05

    # Add volatility (random walk)
    returns = np.random.normal(0, volatility, total_candles)
    price_changes = returns * base_price

    # Cumulative price
    close_prices = base_price + trend + np.cumsum(price_changes)

    # Ensure prices stay positive and reasonable
    close_prices = np.clip(close_prices, base_price * 0.7, base_price * 1.5)

    # Generate OHLC from close
    data = []
    for i, close in enumerate(close_prices):
        # Add some intra-candle movement
        candle_range = close * volatility * np.random.uniform(0.5, 1.5)

        open_price = close + np.random.uniform(-candle_range, candle_range)
        high = max(open_price, close) + abs(np.random.normal(0, candle_range/2))
        low = min(open_price, close) - abs(np.random.normal(0, candle_range/2))

        # Volume (higher during volatile periods)
        base_volume = 1000000
        volume = base_volume * (1 + abs(returns[i]) * 10) * np.random.uniform(0.5, 2.0)

        data.append({
            'timestamp': timestamps[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })

    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)

    return df


def add_market_events(df, event_type='pump'):
    """Add realistic market events (pumps, dumps, consolidation)"""
    df = df.copy()

    if event_type == 'pump':
        # Sudden price increase
        pump_start = len(df) // 3
        pump_duration = len(df) // 20
        pump_magnitude = 0.10  # 10% pump

        for i in range(pump_start, pump_start + pump_duration):
            multiplier = 1 + (pump_magnitude * (i - pump_start) / pump_duration)
            df.iloc[i:, :4] *= multiplier
            df.iloc[i, 4] *= 2  # Double volume during pump

    elif event_type == 'dump':
        # Sudden price decrease
        dump_start = len(df) // 2
        dump_duration = len(df) // 30
        dump_magnitude = 0.08  # 8% dump

        for i in range(dump_start, dump_start + dump_duration):
            multiplier = 1 - (dump_magnitude * (i - dump_start) / dump_duration)
            df.iloc[i:, :4] *= multiplier
            df.iloc[i, 4] *= 3  # Triple volume during dump

    return df


def save_sample_datasets():
    """Generate and save multiple sample datasets"""

    # Create data directory
    os.makedirs('data/sample', exist_ok=True)

    print("🔄 Generating sample historical data...")
    print("=" * 60)

    datasets = [
        {
            'name': 'BTCUSDT_1h_60d_trending',
            'symbol': 'BTCUSDT',
            'start_date': '2024-08-01',
            'days': 60,
            'timeframe': '1h',
            'base_price': 62000,
            'trend': 'up',
            'volatility': 0.015,
            'event': 'pump'
        },
        {
            'name': 'ETHUSDT_15m_45d_balanced',
            'symbol': 'ETHUSDT',
            'start_date': '2024-09-01',
            'days': 45,
            'timeframe': '15m',
            'base_price': 2600,
            'trend': 'sideways',
            'volatility': 0.020,
            'event': None
        },
        {
            'name': 'BNBUSDT_5m_30d_volatile',
            'symbol': 'BNBUSDT',
            'start_date': '2024-10-01',
            'days': 30,
            'timeframe': '5m',
            'base_price': 580,
            'trend': 'up',
            'volatility': 0.025,
            'event': 'dump'
        }
    ]

    for config in datasets:
        print(f"\n📊 Generating {config['name']}...")

        df = generate_realistic_crypto_data(
            symbol=config['symbol'],
            start_date=config['start_date'],
            days=config['days'],
            timeframe=config['timeframe'],
            base_price=config['base_price'],
            trend_direction=config['trend'],
            volatility=config['volatility']
        )

        # Add market event if specified
        if config['event']:
            df = add_market_events(df, config['event'])

        # Save to CSV
        filename = f"data/sample/{config['name']}.csv"
        df.to_csv(filename)

        print(f"   ✅ Saved {len(df):,} candles to {filename}")
        print(f"   📅 Range: {df.index[0]} to {df.index[-1]}")
        print(f"   💰 Price: ${df['close'].iloc[0]:.2f} → ${df['close'].iloc[-1]:.2f} "
              f"({((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:+.2f}%)")

    print("\n" + "=" * 60)
    print("✅ Sample data generation complete!")
    print("\nDatasets created:")
    print("  1. BTCUSDT 1h (60 days) - Uptrending with pump event")
    print("  2. ETHUSDT 15m (45 days) - Sideways/ranging market")
    print("  3. BNBUSDT 5m (30 days) - Volatile with dump event")
    print("\nUse these datasets for backtesting when Binance API is unavailable.")


if __name__ == "__main__":
    save_sample_datasets()
