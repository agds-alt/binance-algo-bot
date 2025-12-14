"""
Historical Data Fetcher
Fetch OHLCV data from Binance for backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import asyncio
import httpx
import time


class DataFetcher:
    """
    Fetch historical kline data from Binance

    Supports both testnet and production
    """

    def __init__(self, use_testnet: bool = False):
        """
        Initialize data fetcher

        Args:
            use_testnet: Use testnet or production API
        """
        self.use_testnet = use_testnet

        if use_testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

    async def fetch_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1500
    ) -> pd.DataFrame:
        """
        Fetch historical klines (OHLCV data)

        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            start_time: Start datetime (default: 30 days ago)
            end_time: End datetime (default: now)
            limit: Max candles per request (max 1500)

        Returns:
            DataFrame with OHLCV data
        """
        # Default time range: last 30 days
        if end_time is None:
            end_time = datetime.utcnow()

        if start_time is None:
            start_time = end_time - timedelta(days=30)

        # Convert to milliseconds
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)

        all_klines = []
        current_start = start_ms

        async with httpx.AsyncClient(timeout=30.0) as client:
            while current_start < end_ms:
                # API parameters
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': current_start,
                    'endTime': end_ms,
                    'limit': limit
                }

                try:
                    # Fetch data
                    response = await client.get(
                        f"{self.base_url}/fapi/v1/klines",
                        params=params
                    )
                    response.raise_for_status()

                    klines = response.json()

                    if not klines:
                        break

                    all_klines.extend(klines)

                    # Update start time for next batch
                    current_start = klines[-1][6] + 1  # Close time + 1ms

                    # Rate limiting (1200 requests/minute = 50ms between requests)
                    await asyncio.sleep(0.05)

                except httpx.HTTPError as e:
                    print(f"Error fetching klines: {e}")
                    break

        # Convert to DataFrame
        if not all_klines:
            return pd.DataFrame()

        df = pd.DataFrame(all_klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])

        # Convert types
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)

        # Set index
        df.set_index('open_time', inplace=True)

        # Keep only necessary columns
        df = df[['open', 'high', 'low', 'close', 'volume']]

        return df

    def fetch_klines_sync(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1500
    ) -> pd.DataFrame:
        """
        Synchronous wrapper for fetch_klines

        Args:
            symbol: Trading pair
            interval: Timeframe
            start_time: Start datetime
            end_time: End datetime
            limit: Max candles per request

        Returns:
            DataFrame with OHLCV data
        """
        return asyncio.run(
            self.fetch_klines(symbol, interval, start_time, end_time, limit)
        )

    async def fetch_multiple_timeframes(
        self,
        symbol: str,
        intervals: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """
        Fetch multiple timeframes concurrently

        Args:
            symbol: Trading pair
            intervals: List of timeframes
            start_time: Start datetime
            end_time: End datetime

        Returns:
            Dict with {interval: DataFrame}
        """
        tasks = [
            self.fetch_klines(symbol, interval, start_time, end_time)
            for interval in intervals
        ]

        results = await asyncio.gather(*tasks)

        return dict(zip(intervals, results))

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for backtesting

        Args:
            df: OHLCV DataFrame

        Returns:
            DataFrame with indicators
        """
        df = df.copy()

        # EMAs
        df['ema_8'] = df['close'].ewm(span=8, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()

        # Volume MA
        df['volume_ma'] = df['volume'].rolling(window=20).mean()

        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)

        return df

    def get_market_hours_filter(self, df: pd.DataFrame) -> pd.Series:
        """
        Filter for preferred market hours (UTC)

        Args:
            df: DataFrame with datetime index

        Returns:
            Boolean series for filtering
        """
        hour = df.index.hour

        # Preferred sessions (from optimized config)
        preferred = (
            ((hour >= 7) & (hour < 10)) |   # London open
            ((hour >= 13) & (hour < 17)) |  # NY open / overlap
            ((hour >= 20) & (hour < 23))    # Asian volatility
        )

        # Avoid sessions
        avoid = (
            ((hour >= 4) & (hour < 6)) |    # Dead zone
            ((hour >= 23) | (hour < 2))     # Low liquidity
        )

        return preferred & ~avoid


# Example usage
if __name__ == "__main__":
    # Initialize fetcher
    fetcher = DataFetcher(use_testnet=False)

    # Fetch BNB/USDT 5m data for last 30 days
    df = fetcher.fetch_klines_sync(
        symbol='BNBUSDT',
        interval='5m',
        start_time=datetime.utcnow() - timedelta(days=30),
        end_time=datetime.utcnow()
    )

    print(f"Fetched {len(df)} candles")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print(f"\nSample data:")
    print(df.head())

    # Calculate indicators
    df_with_indicators = fetcher.calculate_indicators(df)
    print(f"\nIndicators added:")
    print(df_with_indicators.columns.tolist())
