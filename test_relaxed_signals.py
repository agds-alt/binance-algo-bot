#!/usr/bin/env python3
"""
Test script to verify relaxed signal detection algorithm
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from modules.data_fetcher import DataFetcher
from modules.backtester import relaxed_ema_crossover_signals
from modules.config import ALLOWED_PAIRS, SCALPING_CONFIG

def test_signals():
    """Test signal detection on multiple pairs"""
    print("=" * 70)
    print("🧪 TESTING RELAXED SIGNAL DETECTION ALGORITHM")
    print("=" * 70)
    print(f"Testing on: {', '.join(ALLOWED_PAIRS[:5])}")
    print(f"Timeframe: {SCALPING_CONFIG.PRIMARY_TIMEFRAME}")
    print(f"Criteria: 4/6 confirmations, 1.2x volume, 25-75 RSI, 0.3% trend\n")

    fetcher = DataFetcher(use_testnet=False)

    results = []

    for symbol in ALLOWED_PAIRS[:5]:  # Test first 5 pairs
        print(f"\n{'='*70}")
        print(f"📊 Analyzing {symbol}...")
        print(f"{'='*70}")

        try:
            # Fetch recent data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=6)

            df = fetcher.fetch_klines_sync(
                symbol=symbol,
                interval=SCALPING_CONFIG.PRIMARY_TIMEFRAME,
                start_time=start_time,
                end_time=end_time,
                limit=500
            )

            if df.empty or len(df) < 200:
                print(f"❌ Insufficient data for {symbol}")
                continue

            # Calculate indicators
            df = fetcher.calculate_indicators(df)

            # Get signal with debug info
            signal = relaxed_ema_crossover_signals(df, debug=True)

            if signal:
                has_signal = signal.get('has_signal', False)
                conf_count = signal.get('confirmations', 0)
                side = signal.get('side', 'NEUTRAL')
                checks = signal.get('checks', {})

                print(f"\n{'🟢' if has_signal else '🟡'} Signal: {side}")
                print(f"Confirmations: {conf_count}/6 (Need 4+ for signal)")
                print("\nChecks:")
                for check_name, check_value in checks.items():
                    print(f"  {check_name}: {check_value}")

                if has_signal and side != 'NEUTRAL':
                    print(f"\n✅ {side} SIGNAL DETECTED!")
                    print(f"   Entry: ${signal['entry_price']:,.2f}")
                    print(f"   Stop Loss: ${signal['stop_loss']:,.2f}")
                    print(f"   TP1: ${signal['take_profits'][0]:,.2f}")
                    print(f"   TP2: ${signal['take_profits'][1]:,.2f}")
                    print(f"   TP3: ${signal['take_profits'][2]:,.2f}")

                    results.append({
                        'symbol': symbol,
                        'side': side,
                        'confirmations': conf_count,
                        'has_signal': True
                    })
                else:
                    reason = signal.get('reason', 'Not enough confirmations')
                    print(f"\nℹ️  No clear signal - {reason}")

                    results.append({
                        'symbol': symbol,
                        'side': 'NEUTRAL',
                        'confirmations': conf_count,
                        'has_signal': False
                    })
            else:
                print(f"❌ No signal data returned")

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print("📈 SUMMARY")
    print("=" * 70)

    total_scanned = len(results)
    signals_found = sum(1 for r in results if r['has_signal'])

    print(f"\nPairs Scanned: {total_scanned}")
    print(f"Signals Found: {signals_found}")
    print(f"Success Rate: {(signals_found/total_scanned*100) if total_scanned > 0 else 0:.1f}%")

    if signals_found > 0:
        print("\n🎯 Signals Detected:")
        for r in results:
            if r['has_signal']:
                print(f"  • {r['symbol']}: {r['side']} ({r['confirmations']}/6 confirmations)")
    else:
        print("\n⚠️  No signals detected. Market conditions may not be favorable.")
        print("    The relaxed algorithm needs at least 4/6 confirmations.")

    print("\n" + "=" * 70)
    print("✅ Test completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_signals()
