"""
Fixed Real Backtest Runner
Use hardcoded date ranges that we know have data
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_fetcher import DataFetcher
from modules.backtester import (
    Backtester,
    optimized_ema_crossover_signals,
    relaxed_ema_crossover_signals
)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_results(result, scenario_name):
    """Print backtest results"""

    print_section(f"📈 RESULTS: {scenario_name}")

    print(f"\n💰 Performance:")
    print(f"  Return:            ${result.total_return:,.2f} ({result.total_return_percent:+.2f}%)")
    print(f"  Duration:          {result.duration_days} days")

    print(f"\n📊 Trades:")
    print(f"  Total:             {result.total_trades}")
    print(f"  Win Rate:          {result.win_rate:.1f}%")
    print(f"  Profit Factor:     {result.profit_factor:.2f}x")

    print(f"\n⚠️ Risk:")
    print(f"  Max Drawdown:      {result.max_drawdown_percent:.2f}%")
    print(f"  Sharpe Ratio:      {result.sharpe_ratio:.2f}")

    # Assessment
    print(f"\n🎯 Assessment:")
    if result.total_return_percent > 10:
        print(f"  🟢 EXCELLENT return")
    elif result.total_return_percent > 5:
        print(f"  🟡 GOOD return")
    elif result.total_return_percent > 0:
        print(f"  🟠 POSITIVE return")
    else:
        print(f"  🔴 NEGATIVE return")

    if result.win_rate > 55:
        print(f"  🟢 STRONG win rate")
    elif result.win_rate > 50:
        print(f"  🟡 DECENT win rate")
    else:
        print(f"  🔴 LOW win rate")


def run_backtest_with_dates(
    symbol: str,
    timeframe: str,
    start_date: str,  # Format: "YYYY-MM-DD"
    end_date: str,
    strategy_name: str,
    strategy_func,
    initial_capital: float = 10000,
    risk_per_trade: float = 0.015
):
    """Run backtest with specific date range"""

    scenario_name = f"{symbol} {timeframe} - {strategy_name}"

    print_section(f"🚀 RUNNING: {scenario_name}")

    print(f"\n📊 Configuration:")
    print(f"  Symbol:        {symbol}")
    print(f"  Timeframe:     {timeframe}")
    print(f"  Period:        {start_date} to {end_date}")
    print(f"  Strategy:      {strategy_name}")
    print(f"  Capital:       ${initial_capital:,.2f}")
    print(f"  Risk/Trade:    {risk_per_trade*100:.1f}%")

    # Parse dates
    start_time = datetime.strptime(start_date, "%Y-%m-%d")
    end_time = datetime.strptime(end_date, "%Y-%m-%d")

    # Fetch data
    print(f"\n📥 Fetching data...")
    fetcher = DataFetcher(use_testnet=False)

    try:
        df = fetcher.fetch_klines_sync(
            symbol=symbol,
            interval=timeframe,
            start_time=start_time,
            end_time=end_time
        )

        if df.empty:
            print("❌ No data fetched!")
            return None

        print(f"✅ Fetched {len(df):,} candles")

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    # Calculate indicators
    print(f"🔢 Calculating indicators...")
    df = fetcher.calculate_indicators(df)
    print(f"✅ Done")

    # Run backtest
    print(f"⚡ Running backtest...")
    backtester = Backtester(
        initial_capital=initial_capital,
        risk_per_trade=risk_per_trade,
        fee_percent=0.0004,
        slippage_percent=0.0005
    )

    result = backtester.run_backtest(
        df=df,
        symbol=symbol,
        generate_signals_func=strategy_func,
        timeframe=timeframe
    )

    print(f"✅ Completed!")

    # Display results
    print_results(result, scenario_name)

    return result


def main():
    """Run backtests with known good date ranges"""

    print("\n" + "=" * 70)
    print(" 🎯 REAL DATA BACKTEST SUITE")
    print("=" * 70)

    results = {}

    # Use dates we know have data (recent past from 2024)
    # Conservative: BTC 1h for 2 months
    print("\n\n")
    result1 = run_backtest_with_dates(
        symbol="BTCUSDT",
        timeframe="1h",
        start_date="2024-08-01",
        end_date="2024-09-30",
        strategy_name="Optimized EMA",
        strategy_func=optimized_ema_crossover_signals,
        initial_capital=10000,
        risk_per_trade=0.01
    )
    if result1:
        results['Conservative (BTC 1h)'] = result1

    # Balanced: ETH 15m for 45 days
    print("\n\n")
    result2 = run_backtest_with_dates(
        symbol="ETHUSDT",
        timeframe="15m",
        start_date="2024-09-01",
        end_date="2024-10-15",
        strategy_name="Relaxed EMA",
        strategy_func=relaxed_ema_crossover_signals,
        initial_capital=10000,
        risk_per_trade=0.015
    )
    if result2:
        results['Balanced (ETH 15m)'] = result2

    # Aggressive: BNB 5m for 30 days
    print("\n\n")
    result3 = run_backtest_with_dates(
        symbol="BNBUSDT",
        timeframe="5m",
        start_date="2024-10-01",
        end_date="2024-10-30",
        strategy_name="Relaxed EMA",
        strategy_func=relaxed_ema_crossover_signals,
        initial_capital=10000,
        risk_per_trade=0.02
    )
    if result3:
        results['Aggressive (BNB 5m)'] = result3

    # Summary
    if len(results) > 0:
        print_section("📊 COMPARISON")

        print(f"\n{'Scenario':<25} {'Return':<12} {'Win%':<10} {'PF':<8} {'Sharpe':<10} {'DD%':<8}")
        print("-" * 80)

        for name, r in results.items():
            print(f"{name:<25} "
                  f"{r.total_return_percent:>+6.2f}%     "
                  f"{r.win_rate:>5.1f}%    "
                  f"{r.profit_factor:>5.2f}   "
                  f"{r.sharpe_ratio:>6.2f}    "
                  f"{r.max_drawdown_percent:>5.2f}%")

        print_section("💡 RECOMMENDATIONS")

        best = max(results.items(), key=lambda x: x[1].total_return_percent)
        print(f"\n🏆 Best Return: {best[0]} ({best[1].total_return_percent:+.2f}%)")

        # Check criteria
        print(f"\n✅ Live Trading Readiness:")
        for name, r in results.items():
            checks = [
                r.win_rate > 50,
                r.profit_factor > 1.5,
                r.sharpe_ratio > 1.0,
                r.max_drawdown_percent < 20,
                r.total_trades >= 20
            ]
            passed = sum(checks)

            if passed >= 4:
                print(f"  🟢 {name}: {passed}/5 criteria ✅ READY")
            elif passed >= 3:
                print(f"  🟡 {name}: {passed}/5 criteria ⚠️ NEEDS WORK")
            else:
                print(f"  🔴 {name}: {passed}/5 criteria ❌ NOT READY")

        print(f"\n🎯 Next Steps:")
        print(f"  1. Paper trade best strategy for 2 weeks")
        print(f"  2. Compare paper vs backtest results")
        print(f"  3. Start live with $100-500 if consistent")

    print("\n" + "=" * 70)
    print(" ✅ BACKTEST COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
