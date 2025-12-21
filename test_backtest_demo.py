"""
Backtesting Demo dengan Synthetic Data
Shows how the backtesting system works
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.backtester import Backtester, relaxed_ema_crossover_signals


def generate_synthetic_data(days=30, timeframe='5m'):
    """Generate synthetic OHLCV data for testing"""

    # Calculate number of candles
    if timeframe == '5m':
        candles_per_day = 288
    elif timeframe == '15m':
        candles_per_day = 96
    elif timeframe == '1h':
        candles_per_day = 24
    else:
        candles_per_day = 288

    total_candles = days * candles_per_day

    # Generate timestamps
    start_time = datetime(2024, 11, 1)
    timestamps = [start_time + timedelta(minutes=5*i) for i in range(total_candles)]

    # Generate price data with trend + noise
    base_price = 600  # BNB price
    trend = np.linspace(0, 50, total_candles)  # Upward trend
    noise = np.random.randn(total_candles) * 5  # Random fluctuations
    prices = base_price + trend + noise

    # Generate OHLCV
    data = []
    for i, price in enumerate(prices):
        high = price + abs(np.random.randn() * 2)
        low = price - abs(np.random.randn() * 2)
        open_price = price + np.random.randn() * 1
        close = price + np.random.randn() * 1
        volume = np.random.uniform(100000, 500000)

        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })

    df = pd.DataFrame(data, index=pd.DatetimeIndex(timestamps))

    return df


def calculate_indicators(df):
    """Calculate technical indicators"""
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

    return df


def run_demo_backtest():
    """Run a demo backtest"""

    print("=" * 60)
    print("🧪 BACKTESTING DEMO (Synthetic Data)")
    print("=" * 60)

    # Configuration
    symbol = "BNBUSDT"
    timeframe = "5m"
    days = 30
    initial_capital = 10000

    print(f"\n📊 Configuration:")
    print(f"  Symbol: {symbol}")
    print(f"  Timeframe: {timeframe}")
    print(f"  Period: {days} days")
    print(f"  Capital: ${initial_capital:,.2f}")
    print(f"  Strategy: Relaxed EMA Crossover")

    # Generate synthetic data
    print(f"\n📊 Generating synthetic data...")
    df = generate_synthetic_data(days=days, timeframe=timeframe)
    print(f"✅ Generated {len(df)} candles")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")

    # Calculate indicators
    print(f"\n🔢 Calculating indicators...")
    df = calculate_indicators(df)
    print(f"✅ Indicators calculated")

    # Run backtest
    print(f"\n🚀 Running backtest...")
    backtester = Backtester(
        initial_capital=initial_capital,
        risk_per_trade=0.015,    # 1.5% risk
        fee_percent=0.0004,       # 0.04% fee
        slippage_percent=0.0005   # 0.05% slippage
    )

    result = backtester.run_backtest(
        df=df,
        symbol=symbol,
        generate_signals_func=relaxed_ema_crossover_signals,
        timeframe=timeframe
    )

    print(f"✅ Backtest completed!")

    # Display results
    print("\n" + "=" * 60)
    print("📈 BACKTEST RESULTS")
    print("=" * 60)

    print(f"\n💰 Performance:")
    print(f"  Initial Capital: ${result.initial_capital:,.2f}")
    print(f"  Final Capital: ${result.final_capital:,.2f}")
    print(f"  Total Return: ${result.total_return:,.2f} ({result.total_return_percent:.2f}%)")
    print(f"  Duration: {result.duration_days} days")

    print(f"\n📊 Trade Statistics:")
    print(f"  Total Trades: {result.total_trades}")
    print(f"  Winning Trades: {result.winning_trades}")
    print(f"  Losing Trades: {result.losing_trades}")
    print(f"  Win Rate: {result.win_rate:.2f}%")

    print(f"\n💵 P&L Analysis:")
    print(f"  Gross Profit: ${result.gross_profit:,.2f}")
    print(f"  Gross Loss: ${result.gross_loss:,.2f}")
    print(f"  Net Profit: ${result.net_profit:,.2f}")
    print(f"  Profit Factor: {result.profit_factor:.2f}")
    print(f"  Average Win: ${result.average_win:,.2f}")
    print(f"  Average Loss: ${result.average_loss:,.2f}")
    print(f"  Average R-Multiple: {result.average_rr:.2f}R")

    print(f"\n⚠️ Risk Metrics:")
    print(f"  Max Drawdown: ${result.max_drawdown:,.2f} ({result.max_drawdown_percent:.2f}%)")
    print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"  Sortino Ratio: {result.sortino_ratio:.2f}")
    print(f"  Calmar Ratio: {result.calmar_ratio:.2f}")

    # Performance assessment
    print(f"\n🎯 Assessment:")

    if result.total_return_percent > 10:
        print("  Performance: 🟢 EXCELLENT")
    elif result.total_return_percent > 5:
        print("  Performance: 🟡 GOOD")
    elif result.total_return_percent > 0:
        print("  Performance: 🟠 POSITIVE")
    else:
        print("  Performance: 🔴 NEGATIVE")

    if result.win_rate > 60:
        print("  Win Rate: 🟢 EXCELLENT")
    elif result.win_rate > 50:
        print("  Win Rate: 🟡 GOOD")
    else:
        print("  Win Rate: 🔴 NEEDS IMPROVEMENT")

    if result.sharpe_ratio > 2:
        print("  Sharpe Ratio: 🟢 EXCELLENT (>2)")
    elif result.sharpe_ratio > 1:
        print("  Sharpe Ratio: 🟡 GOOD (>1)")
    else:
        print("  Sharpe Ratio: 🔴 POOR (<1)")

    if result.max_drawdown_percent < 10:
        print("  Max Drawdown: 🟢 ACCEPTABLE (<10%)")
    elif result.max_drawdown_percent < 20:
        print("  Max Drawdown: 🟡 MODERATE (10-20%)")
    else:
        print("  Max Drawdown: 🔴 HIGH RISK (>20%)")

    # Show sample trades
    if result.trades:
        print(f"\n📋 Sample Trades (showing {min(5, len(result.trades))}):")
        for i, trade in enumerate(result.trades[:5]):
            pnl_sign = "🟢" if trade['pnl'] > 0 else "🔴"
            print(f"\n  {pnl_sign} Trade #{i+1} ({trade['side']}):")
            print(f"    Entry: {trade['entry_time']} @ ${trade['entry_price']:.2f}")
            print(f"    Exit: {trade['exit_time']} @ ${trade['exit_price']:.2f}")
            print(f"    P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)")
            print(f"    R-Multiple: {trade['r_multiple']:.2f}R")
            print(f"    Reason: {trade['exit_reason']}")

    # Recommendations
    print("\n💡 Key Takeaways:")
    print(f"  ✅ Backtesting system is fully functional")
    print(f"  ✅ Comprehensive metrics calculated")
    print(f"  ✅ Risk management integrated")
    print(f"  ✅ Ready for real data testing")

    print("\n📝 Next Steps:")
    print(f"  1. Run backtest dengan REAL historical data")
    print(f"  2. Test multiple timeframes (5m, 15m, 1h)")
    print(f"  3. Test multiple symbols (BTC, ETH, BNB)")
    print(f"  4. Optimize parameters based on results")
    print(f"  5. Paper trade for 1-2 weeks")
    print(f"  6. Start live trading with small capital")

    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)

    return result


if __name__ == "__main__":
    try:
        result = run_demo_backtest()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
