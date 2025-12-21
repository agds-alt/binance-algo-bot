"""
Test Stochastic RSI Strategy

This script demonstrates the Stochastic RSI mean reversion strategy
on 1-minute timeframe for scalping.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_fetcher import DataFetcher
from modules.backtester import stochastic_rsi_strategy
from modules.config import ALLOWED_PAIRS

def test_stoch_rsi_strategy():
    """Test Stochastic RSI strategy on all pairs"""
    print("=" * 80)
    print("🎯 TESTING STOCHASTIC RSI STRATEGY")
    print("=" * 80)
    print("\nStrategy: Buy when Stoch RSI ≤ 24 (oversold), Sell when Stoch RSI ≥ 80 (overbought)")
    print("Timeframe: 1m (scalping)")
    print("Confirmations Required: 4/6\n")
    print("=" * 80)

    # Initialize data fetcher
    fetcher = DataFetcher(use_testnet=True)

    # Test on all allowed pairs
    for symbol in ALLOWED_PAIRS:
        print(f"\n📊 SCANNING: {symbol}")
        print("-" * 80)

        try:
            # Fetch recent data (1 minute candles, last 2 hours)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=2)

            df = fetcher.fetch_klines_sync(
                symbol=symbol,
                interval='1m',
                start_time=start_time,
                end_time=end_time,
                limit=500
            )

            if df.empty or len(df) < 30:
                print(f"❌ Not enough data for {symbol}")
                continue

            # Calculate indicators
            df = fetcher.calculate_indicators(df)

            # Generate signal
            signal = stochastic_rsi_strategy(df, debug=True)

            # Get current values
            latest = df.iloc[-1]
            stoch_rsi_val = latest.get('stoch_rsi', 0)
            stoch_rsi_k = latest.get('stoch_rsi_k', 0)
            stoch_rsi_d = latest.get('stoch_rsi_d', 0)

            # Display current state
            print(f"Price: ${latest['close']:,.2f}")
            print(f"Stoch RSI: {stoch_rsi_val:.1f}")
            print(f"  K Line: {stoch_rsi_k:.1f}")
            print(f"  D Line: {stoch_rsi_d:.1f}")
            print(f"RSI: {latest['rsi']:.1f}")
            print()

            if signal and signal.get('has_signal'):
                # SIGNAL DETECTED!
                print("✅" * 40)
                print(f"🚨 SIGNAL DETECTED: {signal['side']} 🚨")
                print("✅" * 40)
                print(f"\nConfirmations: {signal['confirmations']}/6")
                print("\nDetailed Checks:")
                for check_name, check_result in signal['checks'].items():
                    print(f"  {check_result}")

                print(f"\n📈 TRADE SETUP:")
                print(f"  Entry: ${signal['entry_price']:,.2f}")
                print(f"  Stop Loss: ${signal['stop_loss']:,.2f}")
                print(f"  TP1: ${signal['take_profits'][0]:,.2f}")
                print(f"  TP2: ${signal['take_profits'][1]:,.2f}")
                print(f"  TP3: ${signal['take_profits'][2]:,.2f}")

                # Calculate risk/reward
                risk = abs(signal['entry_price'] - signal['stop_loss'])
                reward1 = abs(signal['take_profits'][0] - signal['entry_price'])
                rr_ratio = reward1 / risk if risk > 0 else 0
                print(f"\n  Risk: ${risk:,.2f}")
                print(f"  Reward (TP1): ${reward1:,.2f}")
                print(f"  R:R Ratio: {rr_ratio:.2f}:1")
                print()

            elif signal:
                # Signal object exists but no valid signal
                print(f"⚠️ No signal - {signal['confirmations']}/6 confirmations")
                print(f"Reason: {signal.get('reason', 'Unknown')}")
                if signal.get('checks'):
                    print("\nChecks:")
                    for check_name, check_result in signal['checks'].items():
                        print(f"  {check_result}")
            else:
                print("⏸️ No Stochastic RSI extreme detected")
                print(f"   Stoch RSI: {stoch_rsi_val:.1f} (waiting for <24 or >80)")

        except Exception as e:
            print(f"❌ Error scanning {symbol}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ SCAN COMPLETE")
    print("=" * 80)
    print("\nNote: Signals are rare but high probability when they occur!")
    print("Best during: High volatility periods, strong trends bouncing from extremes")
    print("\nTip: Run this script every minute to catch signals as they form")


if __name__ == "__main__":
    test_stoch_rsi_strategy()
