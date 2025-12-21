"""
Run Backtests with Local Sample Data
Workaround for when Binance API is unavailable
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from modules.backtester import (
    Backtester,
    optimized_ema_crossover_signals,
    relaxed_ema_crossover_signals
)
from modules.data_fetcher import DataFetcher


def load_local_data(filename):
    """Load data from local CSV file"""
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    return df


def calculate_indicators(df):
    """Calculate indicators using DataFetcher"""
    fetcher = DataFetcher()
    return fetcher.calculate_indicators(df)


def print_section(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_results(result, name):
    """Print backtest results"""
    print_section(f"📈 {name}")

    print(f"\n💰 Performance:")
    print(f"  Initial Capital:   ${result.initial_capital:,.2f}")
    print(f"  Final Capital:     ${result.final_capital:,.2f}")
    print(f"  Return:            ${result.total_return:,.2f} ({result.total_return_percent:+.2f}%)")
    print(f"  Duration:          {result.duration_days} days")

    print(f"\n📊 Trade Statistics:")
    print(f"  Total Trades:      {result.total_trades}")
    print(f"  Winning:           {result.winning_trades} ({result.win_rate:.1f}%)")
    print(f"  Losing:            {result.losing_trades}")
    print(f"  Profit Factor:     {result.profit_factor:.2f}x")
    print(f"  Avg R-Multiple:    {result.average_rr:.2f}R")

    print(f"\n⚠️ Risk Metrics:")
    print(f"  Max Drawdown:      ${result.max_drawdown:,.2f} ({result.max_drawdown_percent:.2f}%)")
    print(f"  Sharpe Ratio:      {result.sharpe_ratio:.2f}")
    print(f"  Sortino Ratio:     {result.sortino_ratio:.2f}")

    # Assessment
    print(f"\n🎯 Assessment:")

    score = 0
    if result.win_rate > 50:
        print(f"  ✅ Win Rate: {result.win_rate:.1f}% (>50%)")
        score += 1
    else:
        print(f"  ❌ Win Rate: {result.win_rate:.1f}% (<50%)")

    if result.profit_factor > 1.5:
        print(f"  ✅ Profit Factor: {result.profit_factor:.2f} (>1.5)")
        score += 1
    else:
        print(f"  ❌ Profit Factor: {result.profit_factor:.2f} (<1.5)")

    if result.sharpe_ratio > 1.0:
        print(f"  ✅ Sharpe Ratio: {result.sharpe_ratio:.2f} (>1.0)")
        score += 1
    else:
        print(f"  ❌ Sharpe Ratio: {result.sharpe_ratio:.2f} (<1.0)")

    if result.max_drawdown_percent < 20:
        print(f"  ✅ Max Drawdown: {result.max_drawdown_percent:.2f}% (<20%)")
        score += 1
    else:
        print(f"  ❌ Max Drawdown: {result.max_drawdown_percent:.2f}% (>20%)")

    if result.total_trades >= 20:
        print(f"  ✅ Total Trades: {result.total_trades} (>=20)")
        score += 1
    else:
        print(f"  ❌ Total Trades: {result.total_trades} (<20)")

    print(f"\n🏆 Score: {score}/5")

    if score >= 4:
        print(f"  🟢 EXCELLENT - Ready for paper trading")
    elif score >= 3:
        print(f"  🟡 GOOD - Consider optimization")
    else:
        print(f"  🔴 NEEDS IMPROVEMENT - Optimize or change strategy")

    # Show sample trades
    if result.trades and len(result.trades) > 0:
        print(f"\n📋 Sample Trades (first 5):")
        for i, trade in enumerate(result.trades[:5]):
            emoji = "🟢" if trade['pnl'] > 0 else "🔴"
            print(f"\n  {emoji} Trade #{i+1} ({trade['side']}):")
            print(f"      P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:+.2f}%) | {trade['r_multiple']:.2f}R")
            print(f"      Exit: {trade['exit_reason']}")


def run_backtest_on_local_data(
    data_file,
    symbol,
    timeframe,
    strategy_name,
    strategy_func,
    capital=10000,
    risk=0.015
):
    """Run backtest on local data file"""

    print_section(f"🚀 {symbol} {timeframe} - {strategy_name}")

    print(f"\n📂 Loading data from: {data_file}")

    try:
        df = load_local_data(data_file)
        print(f"✅ Loaded {len(df):,} candles")
        print(f"   Range: {df.index[0]} to {df.index[-1]}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

    print(f"\n🔢 Calculating indicators...")
    df = calculate_indicators(df)
    print(f"✅ Indicators calculated")

    print(f"\n⚡ Running backtest...")
    print(f"   Capital: ${capital:,.2f}")
    print(f"   Risk: {risk*100:.1f}% per trade")

    backtester = Backtester(
        initial_capital=capital,
        risk_per_trade=risk,
        fee_percent=0.0004,
        slippage_percent=0.0005
    )

    result = backtester.run_backtest(
        df=df,
        symbol=symbol,
        generate_signals_func=strategy_func,
        timeframe=timeframe
    )

    print(f"✅ Backtest completed!")

    print_results(result, f"{symbol} {timeframe} - {strategy_name}")

    return result


def main():
    """Run all backtests"""

    print("\n" + "=" * 70)
    print(" 🎯 BACKTEST WITH LOCAL DATA")
    print(" (Workaround for Binance API unavailability)")
    print("=" * 70)

    results = {}

    # Scenario 1: BTC 1h - Conservative
    print("\n\n")
    r1 = run_backtest_on_local_data(
        data_file='data/sample/BTCUSDT_1h_60d_trending.csv',
        symbol='BTCUSDT',
        timeframe='1h',
        strategy_name='Optimized EMA',
        strategy_func=optimized_ema_crossover_signals,
        capital=10000,
        risk=0.01
    )
    if r1:
        results['BTC 1h (Optimized)'] = r1

    # Scenario 2: ETH 15m - Balanced
    print("\n\n")
    r2 = run_backtest_on_local_data(
        data_file='data/sample/ETHUSDT_15m_45d_balanced.csv',
        symbol='ETHUSDT',
        timeframe='15m',
        strategy_name='Relaxed EMA',
        strategy_func=relaxed_ema_crossover_signals,
        capital=10000,
        risk=0.015
    )
    if r2:
        results['ETH 15m (Relaxed)'] = r2

    # Scenario 3: BNB 5m - Aggressive
    print("\n\n")
    r3 = run_backtest_on_local_data(
        data_file='data/sample/BNBUSDT_5m_30d_volatile.csv',
        symbol='BNBUSDT',
        timeframe='5m',
        strategy_name='Relaxed EMA',
        strategy_func=relaxed_ema_crossover_signals,
        capital=10000,
        risk=0.02
    )
    if r3:
        results['BNB 5m (Aggressive)'] = r3

    # Summary
    if len(results) > 0:
        print_section("📊 SUMMARY COMPARISON")

        print(f"\n{'Strategy':<25} {'Return':<12} {'Win%':<10} {'PF':<8} {'Sharpe':<10} {'Score':<8}")
        print("-" * 80)

        for name, r in results.items():
            score = sum([
                r.win_rate > 50,
                r.profit_factor > 1.5,
                r.sharpe_ratio > 1.0,
                r.max_drawdown_percent < 20,
                r.total_trades >= 20
            ])

            print(f"{name:<25} "
                  f"{r.total_return_percent:>+6.2f}%     "
                  f"{r.win_rate:>5.1f}%    "
                  f"{r.profit_factor:>5.2f}   "
                  f"{r.sharpe_ratio:>6.2f}    "
                  f"{score}/5")

        print_section("💡 FINAL RECOMMENDATIONS")

        best = max(results.items(), key=lambda x: x[1].total_return_percent)
        print(f"\n🏆 Best Return: {best[0]} ({best[1].total_return_percent:+.2f}%)")

        ready_count = sum(1 for r in results.values() if sum([
            r.win_rate > 50,
            r.profit_factor > 1.5,
            r.sharpe_ratio > 1.0,
            r.max_drawdown_percent < 20,
            r.total_trades >= 20
        ]) >= 4)

        if ready_count > 0:
            print(f"\n✅ {ready_count} strateg{'y' if ready_count == 1 else 'ies'} passed criteria (4/5)")
            print(f"\n🎯 Next Steps:")
            print(f"  1. Paper trade best strategy for 2 weeks")
            print(f"  2. Compare paper vs backtest performance")
            print(f"  3. If consistent, go live with $100-500")
        else:
            print(f"\n⚠️ No strategies passed 4/5 criteria")
            print(f"\n🔧 Recommendations:")
            print(f"  1. Optimize parameters (EMA periods, confirmations)")
            print(f"  2. Try different timeframes")
            print(f"  3. Test with REAL Binance data (fix API access)")
            print(f"  4. Consider different strategies")

        print(f"\n📝 Note: These are SAMPLE/SYNTHETIC data for testing.")
        print(f"   For accurate results, use real Binance historical data.")

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
