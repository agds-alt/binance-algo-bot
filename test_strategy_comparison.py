"""
Strategy Comparison Test
Compare old vs optimized strategy on BTC/USDT
"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from modules.data_fetcher import DataFetcher
from modules.backtester import (
    Backtester,
    simple_ema_crossover_signals,
    optimized_ema_crossover_signals
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_comparison_test(symbol: str = "BTCUSDT", days: int = 30):
    """
    Compare old vs optimized strategy

    Args:
        symbol: Trading pair to test
        days: Number of days to backtest
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 STRATEGY COMPARISON TEST - {symbol}")
    logger.info(f"{'='*70}\n")

    # Fetch data
    logger.info(f"📥 Fetching {days} days of {symbol} data...")
    fetcher = DataFetcher(use_testnet=False)

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    df = fetcher.fetch_klines_sync(
        symbol=symbol,
        interval="5m",
        start_time=start_time,
        end_time=end_time
    )

    if df.empty:
        logger.error("❌ Failed to fetch data")
        return

    # Calculate indicators
    df = fetcher.calculate_indicators(df)
    logger.info(f"✅ Fetched {len(df)} candles from {df.index[0]} to {df.index[-1]}")

    # Test 1: Old strategy
    logger.info("\n" + "="*70)
    logger.info("🔵 Testing OLD Strategy (2 confirmations)")
    logger.info("="*70)

    backtester_old = Backtester(
        initial_capital=10000,
        risk_per_trade=0.015,
        fee_percent=0.0004
    )

    result_old = backtester_old.run_backtest(
        df=df,
        symbol=symbol,
        generate_signals_func=simple_ema_crossover_signals,
        timeframe="5m"
    )

    logger.info("\n📊 OLD Strategy Results:")
    logger.info(f"  Total Trades: {result_old.total_trades}")
    logger.info(f"  Win Rate: {result_old.win_rate:.1f}%")
    logger.info(f"  Total Return: ${result_old.total_return:+,.2f}")
    logger.info(f"  ROI: {result_old.total_return_percent:+.2f}%")
    logger.info(f"  Profit Factor: {result_old.profit_factor:.2f}")
    logger.info(f"  Sharpe Ratio: {result_old.sharpe_ratio:.2f}")
    logger.info(f"  Max Drawdown: {result_old.max_drawdown_percent:.2f}%")

    # Test 2: Optimized strategy
    logger.info("\n" + "="*70)
    logger.info("🟢 Testing OPTIMIZED Strategy (5/6 confirmations)")
    logger.info("="*70)

    backtester_new = Backtester(
        initial_capital=10000,
        risk_per_trade=0.015,
        fee_percent=0.0004
    )

    result_new = backtester_new.run_backtest(
        df=df,
        symbol=symbol,
        generate_signals_func=optimized_ema_crossover_signals,
        timeframe="5m"
    )

    logger.info("\n📊 OPTIMIZED Strategy Results:")
    logger.info(f"  Total Trades: {result_new.total_trades}")
    logger.info(f"  Win Rate: {result_new.win_rate:.1f}%")
    logger.info(f"  Total Return: ${result_new.total_return:+,.2f}")
    logger.info(f"  ROI: {result_new.total_return_percent:+.2f}%")
    logger.info(f"  Profit Factor: {result_new.profit_factor:.2f}")
    logger.info(f"  Sharpe Ratio: {result_new.sharpe_ratio:.2f}")
    logger.info(f"  Max Drawdown: {result_new.max_drawdown_percent:.2f}%")

    # Comparison
    logger.info("\n" + "="*70)
    logger.info("📈 COMPARISON SUMMARY")
    logger.info("="*70)

    trade_reduction = ((result_old.total_trades - result_new.total_trades) / result_old.total_trades * 100) if result_old.total_trades > 0 else 0
    win_rate_improvement = result_new.win_rate - result_old.win_rate
    roi_improvement = result_new.total_return_percent - result_old.total_return_percent
    pf_improvement = result_new.profit_factor - result_old.profit_factor

    logger.info(f"\n📊 Trade Count:")
    logger.info(f"  OLD: {result_old.total_trades} trades")
    logger.info(f"  NEW: {result_new.total_trades} trades")
    logger.info(f"  Reduction: {trade_reduction:+.1f}% {'✅' if trade_reduction > 0 else '⚠️'}")

    logger.info(f"\n📊 Win Rate:")
    logger.info(f"  OLD: {result_old.win_rate:.1f}%")
    logger.info(f"  NEW: {result_new.win_rate:.1f}%")
    logger.info(f"  Improvement: {win_rate_improvement:+.1f}% {'✅' if win_rate_improvement > 0 else '⚠️'}")

    logger.info(f"\n📊 ROI:")
    logger.info(f"  OLD: {result_old.total_return_percent:+.2f}%")
    logger.info(f"  NEW: {result_new.total_return_percent:+.2f}%")
    logger.info(f"  Improvement: {roi_improvement:+.2f}% {'✅' if roi_improvement > 0 else '⚠️'}")

    logger.info(f"\n📊 Profit Factor:")
    logger.info(f"  OLD: {result_old.profit_factor:.2f}")
    logger.info(f"  NEW: {result_new.profit_factor:.2f}")
    logger.info(f"  Improvement: {pf_improvement:+.2f} {'✅' if pf_improvement > 0 else '⚠️'}")

    logger.info(f"\n📊 Sharpe Ratio:")
    logger.info(f"  OLD: {result_old.sharpe_ratio:.2f}")
    logger.info(f"  NEW: {result_new.sharpe_ratio:.2f}")
    logger.info(f"  {'✅ Better' if result_new.sharpe_ratio > result_old.sharpe_ratio else '⚠️ Worse'}")

    # Verdict
    logger.info("\n" + "="*70)
    logger.info("🎯 VERDICT")
    logger.info("="*70)

    improvements = 0
    if result_new.win_rate > result_old.win_rate:
        improvements += 1
    if result_new.total_return_percent > result_old.total_return_percent:
        improvements += 1
    if result_new.profit_factor > result_old.profit_factor:
        improvements += 1
    if result_new.sharpe_ratio > result_old.sharpe_ratio:
        improvements += 1

    if improvements >= 3:
        logger.info("✅ OPTIMIZED strategy is BETTER!")
        logger.info("   Recommendation: Use optimized strategy for live trading")
    elif improvements >= 2:
        logger.info("🟡 OPTIMIZED strategy shows MIXED results")
        logger.info("   Recommendation: Further tuning needed")
    else:
        logger.info("⚠️ OLD strategy performed BETTER")
        logger.info("   Recommendation: Keep testing or use old strategy")

    logger.info("\n" + "="*70)
    logger.info("✅ Comparison test completed!")


if __name__ == "__main__":
    logger.info("🧪 STRATEGY COMPARISON TEST")
    logger.info("Testing: OLD (2 confirmations) vs OPTIMIZED (5/6 confirmations)")
    logger.info("Pair: BTC/USDT | Period: 30 days | Timeframe: 5m\n")

    run_comparison_test(symbol="BTCUSDT", days=30)
