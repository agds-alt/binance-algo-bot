"""
Multi-Pair Trading Test
Test BTC, ETH, and BNB simultaneously
"""

import asyncio
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent))

from test_trading import TestTradingBot
from modules.bot_state_manager import get_bot_state_manager
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_pair(symbol: str, num_trades: int = 5):
    """Test a single trading pair"""
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 TESTING {symbol}")
    logger.info(f"{'='*70}\n")

    bot = TestTradingBot(initial_capital=10000, symbol=symbol)

    try:
        await bot.run_test_trades(num_trades=num_trades)
        return bot.trades_executed
    except Exception as e:
        logger.error(f"❌ Error testing {symbol}: {e}")
        return []


async def main():
    """Test multiple pairs"""
    logger.info("🎯 MULTI-PAIR TRADING TEST")
    logger.info("Testing: BTC, ETH, BNB")
    logger.info("Trades per pair: 5")
    logger.info("")

    # Start bot state
    state_manager = get_bot_state_manager()
    state_manager.start_bot(
        pid=os.getpid(),
        mode="testnet",
        capital=10000
    )

    try:
        # Test each pair sequentially
        pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        results = {}

        for pair in pairs:
            trades = await test_pair(pair, num_trades=5)
            results[pair] = trades

        # Print comparison summary
        logger.info("\n" + "="*70)
        logger.info("📊 MULTI-PAIR COMPARISON")
        logger.info("="*70)

        for pair, trades in results.items():
            if trades:
                total_pnl = sum(t['pnl'] for t in trades)
                win_count = sum(1 for t in trades if t['pnl'] > 0)
                win_rate = (win_count / len(trades) * 100) if trades else 0

                logger.info(f"\n{pair}:")
                logger.info(f"  Trades: {len(trades)}")
                logger.info(f"  Win Rate: {win_rate:.1f}%")
                logger.info(f"  Total P&L: ${total_pnl:+,.2f}")
                logger.info(f"  ROI: {(total_pnl/10000*100):+.2f}%")

        logger.info("\n" + "="*70)
        logger.info("✅ Multi-pair test completed!")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        state_manager.stop_bot()


if __name__ == "__main__":
    logger.info("🧪 TEST MODE - Simulated trades, no real orders placed!")
    logger.info("📊 Fetching real market data from Binance\n")

    asyncio.run(main())
