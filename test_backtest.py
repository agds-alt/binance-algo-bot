"""
Quick Backtest Test
Run a sample backtest to verify the system works
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_fetcher import DataFetcher
from modules.backtester import Backtester, relaxed_ema_crossover_signals, optimized_ema_crossover_signals

def run_test_backtest():
    """Run a test backtest on BNB/USDT"""

    print("=" * 60)
    print("🧪 RUNNING TEST BACKTEST")
    print("=" * 60)

    # Configuration
    symbol = "BNBUSDT"
    timeframe = "5m"
    days_back = 30
    initial_capital = 10000

    print(f"\n📊 Configuration:")
    print(f"  Symbol: {symbol}")
    print(f"  Timeframe: {timeframe}")
    print(f"  Period: {days_back} days")
    print(f"  Capital: ${initial_capital}")

    # Fetch data
    print(f"\n📥 Fetching {days_back} days of {symbol} data...")
    fetcher = DataFetcher(use_testnet=False)

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_back)

    df = fetcher.fetch_klines_sync(
        symbol=symbol,
        interval=timeframe,
        start_time=start_time,
        end_time=end_time
    )

    if df.empty:
        print("❌ Failed to fetch data!")
        return

    print(f"✅ Fetched {len(df)} candles")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")

    # Calculate indicators
    print("\n🔢 Calculating indicators...")
    df = fetcher.calculate_indicators(df)
    print("✅ Indicators calculated")

    # Run backtest with RELAXED strategy
    print("\n🚀 Running backtest (Relaxed EMA strategy)...")
    backtester = Backtester(
        initial_capital=initial_capital,
        risk_per_trade=0.015,  # 1.5%
        fee_percent=0.0004,     # 0.04%
        slippage_percent=0.0005 # 0.05%
    )

    result = backtester.run_backtest(
        df=df,
        symbol=symbol,
        generate_signals_func=relaxed_ema_crossover_signals,
        timeframe=timeframe
    )

    print("✅ Backtest completed!")

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
        print("  Sharpe Ratio: 🟢 EXCELLENT")
    elif result.sharpe_ratio > 1:
        print("  Sharpe Ratio: 🟡 GOOD")
    else:
        print("  Sharpe Ratio: 🔴 POOR")

    if result.max_drawdown_percent < 10:
        print("  Max Drawdown: 🟢 ACCEPTABLE")
    elif result.max_drawdown_percent < 20:
        print("  Max Drawdown: 🟡 MODERATE")
    else:
        print("  Max Drawdown: 🔴 HIGH RISK")

    # Recommendations
    print("\n💡 Recommendations:")

    if result.total_trades < 10:
        print("  ⚠️ Not enough trades for statistical significance")
        print("     → Run longer backtest (60-90 days)")

    if result.win_rate < 50:
        print("  ⚠️ Win rate below 50%")
        print("     → Need higher profit factor (>2) to be profitable")

    if result.profit_factor < 1.5:
        print("  ⚠️ Profit factor too low")
        print("     → Consider stricter entry criteria or better exits")

    if result.max_drawdown_percent > 15:
        print("  ⚠️ High drawdown risk")
        print("     → Reduce position size or improve risk management")

    if result.sharpe_ratio < 1:
        print("  ⚠️ Low risk-adjusted returns")
        print("     → Strategy may not be worth the risk")

    # Show sample trades
    if result.trades:
        print(f"\n📋 Sample Trades (first 5):")
        for i, trade in enumerate(result.trades[:5]):
            print(f"\n  Trade #{i+1}:")
            print(f"    Entry: {trade['entry_time']} @ ${trade['entry_price']:.2f}")
            print(f"    Exit: {trade['exit_time']} @ ${trade['exit_price']:.2f}")
            print(f"    Side: {trade['side']}")
            print(f"    P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)")
            print(f"    R-Multiple: {trade['r_multiple']:.2f}R")
            print(f"    Reason: {trade['exit_reason']}")

    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)

    return result


if __name__ == "__main__":
    try:
        result = run_test_backtest()
    except Exception as e:
        print(f"\n❌ Error running backtest: {e}")
        import traceback
        traceback.print_exc()
