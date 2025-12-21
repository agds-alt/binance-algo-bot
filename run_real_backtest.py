"""
Real Backtest Runner
Fetch real historical data from Binance and run comprehensive backtests
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
    relaxed_ema_crossover_signals,
    stochastic_rsi_strategy
)


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_results(result, scenario_name):
    """Print backtest results in formatted way"""

    print_section(f"📈 RESULTS: {scenario_name}")

    print(f"\n💰 Performance Overview:")
    print(f"  Initial Capital:    ${result.initial_capital:,.2f}")
    print(f"  Final Capital:      ${result.final_capital:,.2f}")
    print(f"  Total Return:       ${result.total_return:,.2f} ({result.total_return_percent:+.2f}%)")
    print(f"  Duration:           {result.duration_days} days")

    print(f"\n📊 Trade Statistics:")
    print(f"  Total Trades:       {result.total_trades}")
    print(f"  Winning Trades:     {result.winning_trades} ({result.win_rate:.1f}%)")
    print(f"  Losing Trades:      {result.losing_trades}")
    print(f"  Profit Factor:      {result.profit_factor:.2f}x")

    print(f"\n💵 P&L Breakdown:")
    print(f"  Gross Profit:       ${result.gross_profit:,.2f}")
    print(f"  Gross Loss:         ${result.gross_loss:,.2f}")
    print(f"  Net Profit:         ${result.net_profit:,.2f}")
    print(f"  Average Win:        ${result.average_win:,.2f}")
    print(f"  Average Loss:       ${result.average_loss:,.2f}")
    print(f"  Avg R-Multiple:     {result.average_rr:.2f}R")

    print(f"\n⚠️ Risk Metrics:")
    print(f"  Max Drawdown:       ${result.max_drawdown:,.2f} ({result.max_drawdown_percent:.2f}%)")
    print(f"  Sharpe Ratio:       {result.sharpe_ratio:.2f}")
    print(f"  Sortino Ratio:      {result.sortino_ratio:.2f}")
    print(f"  Calmar Ratio:       {result.calmar_ratio:.2f}")

    # Assessment
    print(f"\n🎯 Performance Assessment:")

    # Overall return
    if result.total_return_percent > 15:
        print(f"  Return:             🟢 EXCELLENT ({result.total_return_percent:+.2f}%)")
    elif result.total_return_percent > 10:
        print(f"  Return:             🟢 VERY GOOD ({result.total_return_percent:+.2f}%)")
    elif result.total_return_percent > 5:
        print(f"  Return:             🟡 GOOD ({result.total_return_percent:+.2f}%)")
    elif result.total_return_percent > 0:
        print(f"  Return:             🟠 POSITIVE ({result.total_return_percent:+.2f}%)")
    else:
        print(f"  Return:             🔴 NEGATIVE ({result.total_return_percent:+.2f}%)")

    # Win rate
    if result.win_rate > 60:
        print(f"  Win Rate:           🟢 EXCELLENT ({result.win_rate:.1f}%)")
    elif result.win_rate > 50:
        print(f"  Win Rate:           🟡 GOOD ({result.win_rate:.1f}%)")
    elif result.win_rate > 45:
        print(f"  Win Rate:           🟠 ACCEPTABLE ({result.win_rate:.1f}%)")
    else:
        print(f"  Win Rate:           🔴 POOR ({result.win_rate:.1f}%)")

    # Profit factor
    if result.profit_factor > 2.0:
        print(f"  Profit Factor:      🟢 EXCELLENT ({result.profit_factor:.2f}x)")
    elif result.profit_factor > 1.5:
        print(f"  Profit Factor:      🟡 GOOD ({result.profit_factor:.2f}x)")
    elif result.profit_factor > 1.0:
        print(f"  Profit Factor:      🟠 ACCEPTABLE ({result.profit_factor:.2f}x)")
    else:
        print(f"  Profit Factor:      🔴 UNPROFITABLE ({result.profit_factor:.2f}x)")

    # Sharpe ratio
    if result.sharpe_ratio > 2:
        print(f"  Sharpe Ratio:       🟢 EXCELLENT ({result.sharpe_ratio:.2f})")
    elif result.sharpe_ratio > 1:
        print(f"  Sharpe Ratio:       🟡 GOOD ({result.sharpe_ratio:.2f})")
    elif result.sharpe_ratio > 0:
        print(f"  Sharpe Ratio:       🟠 ACCEPTABLE ({result.sharpe_ratio:.2f})")
    else:
        print(f"  Sharpe Ratio:       🔴 POOR ({result.sharpe_ratio:.2f})")

    # Max drawdown
    if result.max_drawdown_percent < 10:
        print(f"  Max Drawdown:       🟢 LOW RISK ({result.max_drawdown_percent:.2f}%)")
    elif result.max_drawdown_percent < 15:
        print(f"  Max Drawdown:       🟡 ACCEPTABLE ({result.max_drawdown_percent:.2f}%)")
    elif result.max_drawdown_percent < 25:
        print(f"  Max Drawdown:       🟠 MODERATE ({result.max_drawdown_percent:.2f}%)")
    else:
        print(f"  Max Drawdown:       🔴 HIGH RISK ({result.max_drawdown_percent:.2f}%)")

    # Show sample trades
    if result.trades and len(result.trades) > 0:
        print(f"\n📋 Sample Trades (first 3 & last 2):")

        # First 3
        for i, trade in enumerate(result.trades[:3]):
            pnl_emoji = "🟢" if trade['pnl'] > 0 else "🔴"
            print(f"\n  {pnl_emoji} Trade #{i+1} ({trade['side']}):")
            print(f"      Entry: {str(trade['entry_time'])[:19]} @ ${trade['entry_price']:.2f}")
            print(f"      Exit:  {str(trade['exit_time'])[:19]} @ ${trade['exit_price']:.2f}")
            print(f"      P&L:   ${trade['pnl']:.2f} ({trade['pnl_percent']:+.2f}%) | {trade['r_multiple']:.2f}R")
            print(f"      Exit:  {trade['exit_reason']}")

        # Last 2
        if len(result.trades) > 5:
            print(f"\n  ... ({len(result.trades) - 5} trades omitted) ...")

            for i, trade in enumerate(result.trades[-2:], len(result.trades)-2):
                pnl_emoji = "🟢" if trade['pnl'] > 0 else "🔴"
                print(f"\n  {pnl_emoji} Trade #{i+1} ({trade['side']}):")
                print(f"      Entry: {str(trade['entry_time'])[:19]} @ ${trade['entry_price']:.2f}")
                print(f"      Exit:  {str(trade['exit_time'])[:19]} @ ${trade['exit_price']:.2f}")
                print(f"      P&L:   ${trade['pnl']:.2f} ({trade['pnl_percent']:+.2f}%) | {trade['r_multiple']:.2f}R")
                print(f"      Exit:  {trade['exit_reason']}")


def run_backtest_scenario(
    symbol: str,
    timeframe: str,
    days: int,
    strategy_name: str,
    strategy_func,
    initial_capital: float = 10000,
    risk_per_trade: float = 0.015
):
    """Run a single backtest scenario"""

    scenario_name = f"{symbol} {timeframe} ({days}d) - {strategy_name}"

    print_section(f"🚀 RUNNING: {scenario_name}")

    print(f"\n📊 Configuration:")
    print(f"  Symbol:             {symbol}")
    print(f"  Timeframe:          {timeframe}")
    print(f"  Period:             {days} days")
    print(f"  Strategy:           {strategy_name}")
    print(f"  Initial Capital:    ${initial_capital:,.2f}")
    print(f"  Risk per Trade:     {risk_per_trade*100:.1f}%")

    # Fetch data
    print(f"\n📥 Fetching historical data...")
    fetcher = DataFetcher(use_testnet=False)

    # Use proper date calculation
    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    print(f"   From: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   To:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        df = fetcher.fetch_klines_sync(
            symbol=symbol,
            interval=timeframe,
            start_time=start_time,
            end_time=end_time
        )

        if df.empty:
            print("❌ Failed to fetch data!")
            return None

        print(f"✅ Fetched {len(df):,} candles")
        print(f"   Range: {df.index[0]} to {df.index[-1]}")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

    # Calculate indicators
    print(f"\n🔢 Calculating indicators...")
    df = fetcher.calculate_indicators(df)
    print(f"✅ Indicators calculated")

    # Run backtest
    print(f"\n⚡ Running backtest...")
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

    print(f"✅ Backtest completed!")

    # Display results
    print_results(result, scenario_name)

    return result


def main():
    """Run multiple backtest scenarios"""

    print("\n" + "=" * 70)
    print(" 🎯 COMPREHENSIVE BACKTEST SUITE")
    print(" Testing 3 scenarios with REAL historical data")
    print("=" * 70)

    results = {}

    # Scenario 1: Conservative (BTC 1h)
    print("\n\n")
    result1 = run_backtest_scenario(
        symbol="BTCUSDT",
        timeframe="1h",
        days=60,
        strategy_name="Optimized EMA (5/6 confirmations)",
        strategy_func=optimized_ema_crossover_signals,
        initial_capital=10000,
        risk_per_trade=0.01  # 1% risk
    )
    if result1:
        results['Conservative (BTC 1h)'] = result1

    # Scenario 2: Balanced (ETH 15m)
    print("\n\n")
    result2 = run_backtest_scenario(
        symbol="ETHUSDT",
        timeframe="15m",
        days=45,
        strategy_name="Relaxed EMA (4/6 confirmations)",
        strategy_func=relaxed_ema_crossover_signals,
        initial_capital=10000,
        risk_per_trade=0.015  # 1.5% risk
    )
    if result2:
        results['Balanced (ETH 15m)'] = result2

    # Scenario 3: Aggressive (BNB 5m)
    print("\n\n")
    result3 = run_backtest_scenario(
        symbol="BNBUSDT",
        timeframe="5m",
        days=30,
        strategy_name="Stochastic RSI (Mean Reversion)",
        strategy_func=stochastic_rsi_strategy,
        initial_capital=10000,
        risk_per_trade=0.02  # 2% risk
    )
    if result3:
        results['Aggressive (BNB 5m)'] = result3

    # Summary comparison
    if len(results) > 0:
        print_section("📊 SUMMARY COMPARISON")

        print(f"\n{'Scenario':<30} {'Return':<12} {'Win Rate':<12} {'PF':<8} {'Sharpe':<10} {'DD':<10}")
        print("-" * 90)

        for name, result in results.items():
            print(f"{name:<30} "
                  f"{result.total_return_percent:>+6.2f}%     "
                  f"{result.win_rate:>5.1f}%      "
                  f"{result.profit_factor:>5.2f}   "
                  f"{result.sharpe_ratio:>6.2f}    "
                  f"{result.max_drawdown_percent:>5.2f}%")

        # Final recommendation
        print_section("💡 FINAL RECOMMENDATIONS")

        best_return = max(results.items(), key=lambda x: x[1].total_return_percent)
        best_sharpe = max(results.items(), key=lambda x: x[1].sharpe_ratio)
        lowest_dd = min(results.items(), key=lambda x: x[1].max_drawdown_percent)

        print(f"\n🏆 Best Overall Return:  {best_return[0]} ({best_return[1].total_return_percent:+.2f}%)")
        print(f"📈 Best Risk-Adjusted:   {best_sharpe[0]} (Sharpe: {best_sharpe[1].sharpe_ratio:.2f})")
        print(f"🛡️  Lowest Risk:          {lowest_dd[0]} (DD: {lowest_dd[1].max_drawdown_percent:.2f}%)")

        # Check if any strategy is good enough for live trading
        print(f"\n✅ Ready for Live Trading?")

        ready_strategies = []
        for name, result in results.items():
            checks = {
                'win_rate': result.win_rate > 50,
                'profit_factor': result.profit_factor > 1.5,
                'sharpe': result.sharpe_ratio > 1.0,
                'drawdown': result.max_drawdown_percent < 20,
                'trades': result.total_trades >= 20
            }

            passed = sum(checks.values())

            if passed >= 4:
                ready_strategies.append((name, result, passed))
                print(f"\n  🟢 {name}:")
                print(f"     ✅ {passed}/5 criteria passed")
                print(f"     Win Rate: {result.win_rate:.1f}% | PF: {result.profit_factor:.2f} | Sharpe: {result.sharpe_ratio:.2f}")
                print(f"     → Recommended for paper trading first")
            elif passed >= 3:
                print(f"\n  🟡 {name}:")
                print(f"     ⚠️ {passed}/5 criteria passed")
                print(f"     → Needs optimization before live trading")
            else:
                print(f"\n  🔴 {name}:")
                print(f"     ❌ Only {passed}/5 criteria passed")
                print(f"     → NOT recommended for live trading")

        if not ready_strategies:
            print(f"\n⚠️ RECOMMENDATION: None of the strategies meet minimum criteria.")
            print(f"   Next steps:")
            print(f"   1. Optimize parameters (EMA periods, RSI thresholds, etc)")
            print(f"   2. Test different timeframes")
            print(f"   3. Try different market conditions (trending vs ranging)")
            print(f"   4. Consider combining strategies")
        else:
            print(f"\n🎯 NEXT STEPS:")
            print(f"   1. Paper trade best strategy for 2 weeks")
            print(f"   2. Monitor performance vs backtest")
            print(f"   3. If consistent, start live with $100-500")
            print(f"   4. Scale up gradually as confidence builds")

    print("\n" + "=" * 70)
    print(" ✅ BACKTEST SUITE COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Backtest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
